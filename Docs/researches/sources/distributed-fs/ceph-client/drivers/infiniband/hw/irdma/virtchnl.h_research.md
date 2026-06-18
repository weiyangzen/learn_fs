# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.h

## Purpose

`virtchnl.h` defines the IRDMA virtual-channel ABI used between a non-privileged RDMA function and its privileged peer. It assigns channel and operation versions, operation codes, register and register-field IDs, packed request and response buffer formats, HMC/vport/vector/capability payloads, initialization parameters, and public request helper prototypes.

## Important APIs, Types, and Functions

- Channel version constants restrict the supported channel to version 2, with legacy version 0 explicitly documented as unsupported.
- Operation-version constants define per-operation payload revisions for HMC get/put, register layout, queue-vector map/unmap, vport add/delete, and RDMA capabilities.
- `enum irdma_vchnl_ops` assigns the wire operation codes for version, HMC function, register layout, capabilities, queue-vector mapping, and vport management.
- Register IDs such as `IRDMA_VCHNL_REG_ID_CQPTAIL`, `IRDMA_VCHNL_REG_ID_CQPDB`, and `IRDMA_VCHNL_REG_ID_DB_ADDR_OFFSET` abstract PF-provided MMIO layout. `IRDMA_VCHNL_REG_PAGE_REL` marks page-relative offsets.
- Register-field IDs such as `IRDMA_VCHNL_REGFLD_ID_CCQPSTATUS_CQP_OP_ERR` and `IRDMA_VCHNL_REGFLD_ID_COMMIT_FPM_CQCNT` abstract hardware bit shifts/masks.
- Packed payloads include `irdma_vchnl_req_hmc_info`, `irdma_vchnl_resp_hmc_info`, `irdma_vchnl_op_buf`, `irdma_vchnl_resp_buf`, and `irdma_vchnl_rdma_caps`.
- Flexible-array vector/vport structures include `irdma_vchnl_qvlist_info`, `irdma_vchnl_qv_info`, `irdma_vchnl_req_vport_info`, and `irdma_vchnl_resp_vport_info`.
- `irdma_vchnl_init_info`, `irdma_vchnl_req`, and `irdma_vchnl_req_init_info` are local driver control structures used to initialize and issue requests.
- Public prototypes expose initialization, version/capability/HMC/register/vector/vport requests, and response parsing.

## Control Flow

The header defines the shape consumed by `virtchnl.c`: callers fill `irdma_vchnl_req_init_info` with operation code, operation version, optional request payload, and optional response buffer. `virtchnl.c` serializes that into `irdma_vchnl_op_buf`, sends it through the hardware-specific transport, receives `irdma_vchnl_resp_buf`, and copies the packed `buf[]` into the expected typed payload.

Register layout flow uses arrays of `irdma_vchnl_reg_info` followed by `irdma_vchnl_reg_field_info`, terminated by invalid IDs. Capability flow returns `irdma_vchnl_rdma_caps`, whose minimum response size can be as small as one byte for forward-compatible extension. HMC and vport responses return scheduler handles for each user priority.

## State and Persistence

The header has no executable state. It defines wire-compatible packed structures and local request descriptors. Fields such as `op_ctx`, `buf_len`, `op_ret`, `hmc_func`, `qs_handle`, `hw_rev`, `cqp_timeout_s`, and register offsets become runtime state in `struct irdma_sc_dev` after `virtchnl.c` processes them.

## Dependencies and Integration Points

The file includes `hmc.h` and `irdma.h` for HMC, hardware generation, and priority constants. It forward-declares `struct irdma_qos` and uses `struct irdma_sc_dev` from the wider driver. The definitions integrate with `virtchnl.c`, gen3 hardware-specific channel transport, device initialization, interrupt vector setup, GSI/vport setup, and CQP timeout tuning in `utils.c`.

## Risks

This header is an ABI contract. Changing packed structure layout, operation IDs, version constants, or register/field IDs can break PF/VF interoperability. Flexible-array sizes must be computed with `struct_size` by callers. Because response capability minimum size is intentionally small, consumers must tolerate missing future fields and keep defaults sane. Packed unaligned structures require careful copying rather than direct assumptions about natural alignment.

## Test Signals

Compile and ABI tests should check structure sizes, packed offsets, operation ID stability, register ID translation coverage, `struct_size` calculations for vector lists, and version min/max behavior. Runtime tests should confirm that every public prototype has a matching implementation and that PF/VF peers using the declared version and payloads can negotiate caps, register layout, HMC function, queue-vector mapping, and vport add/delete successfully.
