# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.c

## Purpose

`virtchnl.c` implements the IRDMA virtual-channel client used by non-privileged functions, especially gen3 VF-style devices, to negotiate capabilities and request privileged PF-mediated setup. It sends synchronous virtual-channel operations, validates responses, translates PF-provided register layouts and bit-field masks into local hardware tables, obtains/releases HMC function IDs, maps AEQ/CEQ queues to interrupt vectors, manages vports, and reads RDMA capabilities.

## Important APIs, Types, and Functions

- `irdma_sc_vchnl_init` initializes virtual-channel state in `struct irdma_sc_dev`, negotiates channel version for non-privileged devices, fetches capabilities, and updates hardware revision.
- Static `vchnl_reg_map` and `vchnl_regfld_map` translate virtual-channel register and field IDs into local `hw_regs`, `hw_masks`, and `hw_shifts` indexes.
- `irdma_alloc_vchnl_req_msg`, `irdma_free_vchnl_req_msg`, `irdma_vchnl_req_send_sync`, `irdma_vchnl_req_verify_resp`, and `irdma_vchnl_req_get_resp` implement common request allocation, serialization, send, response validation, and response copyout.
- `irdma_vchnl_req_get_reg_layout` parses PF-provided register offsets and field descriptions, resolves MMIO addresses, and initializes doorbell pointers.
- `irdma_vchnl_req_get_ver`, `irdma_vchnl_req_get_caps`, `irdma_vchnl_req_get_hmc_fcn`, and `irdma_vchnl_req_put_hmc_fcn` negotiate channel/device capabilities and HMC ownership.
- `irdma_vchnl_req_aeq_vec_map`, `irdma_vchnl_req_ceq_vec_map`, `irdma_vchnl_req_add_vport`, and `irdma_vchnl_req_del_vport` request vector and vport resource configuration from the privileged peer.

## Control Flow

Initialization marks the channel up, stores privilege and PF/VF role, and seeds the requested hardware revision. Privileged devices do not need channel negotiation. Non-privileged devices first send `GET_VER` with the maximum supported channel version, reject peers below the minimum supported version, then send `GET_RDMA_CAPS`; the returned hardware revision replaces the initial revision after range validation.

Every request is built into a fixed-size zeroed `IRDMA_VCHNL_MAX_MSG_SIZE` buffer. The op context is the address of the stack `irdma_vchnl_req`, request payload is copied into `op_buf->buf`, and `irdma_vchnl_req_send_sync` serializes access with `dev->vchnl_mutex` before calling `ig3rdma_vchnl_send_sync`. The received buffer and length are stored in `dev->vc_recv_buf` and `dev->vc_recv_len`, then `irdma_vchnl_req_get_resp` verifies that the response context matches, clamps response data to the caller-provided response buffer, validates size rules for the operation, checks `op_ret`, and copies response payload.

Register-layout parsing reads a sequence of `irdma_vchnl_reg_info` records until an invalid ID. Known IDs are mapped to local hardware register indexes; DB offset and page-relative records are stored as offsets, while BAR-relative records are resolved through `ig3rdma_get_reg_addr`. Doorbell pointers such as `wqe_alloc_db`, `cq_arm_db`, `aeq_alloc_db`, `cqp_db`, and `cq_ack_db` are derived from the populated register table. The following field records are mapped into masks and shifts after validating nonzero bit widths and at most 64 total bits.

HMC and vport operations are small structured requests. Gen3 `GET_HMC_FCN` includes protocol and receives an HMC function ID plus QoS scheduler handles. `ADD_VPORT` and `DEL_VPORT` send vport/QP1 IDs; add-vport copies returned scheduler handles into the provided QoS array. AEQ and CEQ vector mapping allocate a one-vector flexible array request, set the unused queue index to `IRDMA_Q_INVALID_IDX`, and request `QUEUE_VECTOR_MAP`.

## State and Persistence

State is runtime-only and stored in `struct irdma_sc_dev`: channel-up flag, privilege/PF flags, channel version, capabilities, receive buffer length, hardware revision, HMC function ID, QoS handles, register pointer table, mask/shift tables, and doorbell pointers. Requests are temporary heap buffers. The only persistence outside memory is the PF/peer's hardware configuration changed by the virtual-channel operation.

## Dependencies and Integration Points

The file depends on low-level IRDMA hardware definitions, HMC definitions, `ig3rdma_vchnl_send_sync`, `ig3rdma_get_reg_addr`, work-scheduler/QoS structures, and `to_ibdev` logging from `utils.c`. It is called during control-device initialization, gen3 GSI/vport setup and teardown from `verbs.c`/`utils.c`, and interrupt/vector setup code elsewhere in the driver.

## Risks

Virtual-channel parsing is a trust boundary between privileged and non-privileged functions. Response context, length, op return, register IDs, field IDs, bit widths, and register address resolution must be validated before mutating hardware tables. The fixed max message size prevents unbounded allocation but does not by itself prove payload lengths are semantically correct. `resp_len` arithmetic depends on a valid received length at least as large as the response header. Register layout parsing must not accept invalid masks or NULL MMIO addresses, because later MMIO writes would fault or hit wrong registers. The mutex is essential because shared `vc_recv_buf` and `vc_recv_len` are per-device scratch state.

## Test Signals

Useful tests include version negotiation success/failure, unsupported hardware revision rejection, response op-context mismatch, short/oversized response validation, PF error propagation through `op_ret`, register layouts with invalid IDs and invalid bit widths, page-relative versus BAR-relative register mapping, HMC function get/put, QoS handle propagation, AEQ/CEQ vector mapping request shapes, vport add/delete rollback in GSI setup, and concurrent virtual-channel callers proving mutex serialization.
