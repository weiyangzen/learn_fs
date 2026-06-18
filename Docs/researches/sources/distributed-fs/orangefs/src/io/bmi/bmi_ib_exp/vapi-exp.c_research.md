# sources/distributed-fs/orangefs/src/io/bmi/bmi_ib_exp/vapi-exp.c

## Purpose
Implements the legacy Mellanox VAPI provider backend for the experimental BMI InfiniBand method. It mirrors the OpenIB backend for older VAPI/EVAPI stacks: HCA discovery, PD/CQ setup, QP creation and transitions, eager buffer registration, SEND/RECV/RDMA_WRITE posting, completion conversion, memory registration, and pipe-based event forwarding.

## Important APIs, Types, And Functions
Provider state is stored in `struct vapi_device_priv` and `struct vapi_connection_priv`. Major functions include `vapi_ib_initialize`, `vapi_ib_finalize`, `vapi_new_connection`, `exchange_data`, `verify_prop_caps`, `init_connection_modify_qp`, `vapi_drain_qp`, `vapi_close_connection`, `vapi_post_sr`, `vapi_post_rr`, `vapi_post_sr_rdmaw`, `vapi_check_cq`, `vapi_prepare_cq_block`, `vapi_ack_cq_completion_event`, `vapi_wc_status_string`, `vapi_wc_status_to_bmi`, `vapi_mem_register`, `vapi_mem_deregister`, `error_verrno`, `async_event_handler`, `cq_event_handler`, `reinit_mosal`, and `vapi_check_async_events`.

## Control Flow
Initialization reinitializes MOSAL state to survive daemon fork behavior, lists HCAs through EVAPI, chooses the first HCA, installs callback functions in `ib_device->func`, obtains an HCA handle, registers an async handler, verifies port state, allocates a PD, creates a CQ, builds nonblocking pipes for CQ and async events, registers the CQ event handler, and initializes scratch SGE limits for the first connection.

`vapi_new_connection` registers eager receive and send buffers, creates an RC QP, verifies global SGE/outstanding-WR assumptions, exchanges LID and QP number over TCP, transitions the QP through INIT/RTR/RTS, posts initial receive buffers, and performs a final synchronization. `vapi_post_sr` and `vapi_post_rr` submit protocol SENDs and eager RECVs. `vapi_post_sr_rdmaw` decodes CTS descriptors and issues gathered RDMA writes over possibly multiple WRs, signaling the final WR so generic code can advance to RTS_DONE. Completion polling maps VAPI CQE opcodes into `BMI_IB_OP_SEND`, `BMI_IB_OP_RECV`, and `BMI_IB_OP_RDMA_WRITE`.

## State And Persistence
Device state persists in the HCA handle, CQ, PD, local LID, scratch SGE array, outstanding-WR caps, event handler handles, and pipe fds. Per connection, the backend stores QP handle/number, eager MR handles and lkeys, unsignaled counter, remote LID, and remote QP number. Registered memory keys are stored in the generic memcache entries.

## Dependencies And Integration Points
This file depends on VAPI/EVAPI headers, optional `wrap_common.h`, `libmosal.so` symbols through `dlopen`/`dlsym`, OrangeFS byte swapping and internal formatting, and shared BMI IB helpers. It is selected by `BUILD_IB`, while `ib-exp.c` calls it only if the OpenIB initializer did not succeed or was not compiled.

## Risks And Test Signals
VAPI is legacy and contains several environment-specific hacks. `reinit_mosal` reaches into libmosal internals or exported ioctl functions and can fail hard if library symbols differ. VAPI-specific fatal errors call `exit(1)` through `error_verrno`, unlike generic `error()`. Event handlers write to pipes from callback threads and can fail if pipes fill. The code ignores the `options` argument and always uses `VAPI_PORT`. As with OpenIB, disabled bounce-buffer branches may be stale. Test signals include VAPI-only build/link on a matching stack, daemon fork/startup, HCA absence/multiple-HCA behavior, port inactive errors, TCP QP exchange, CQ/async pipe event delivery, RDMA scatter/gather transfers, retry-exceeded error mapping, and clean handler/pipe teardown.
