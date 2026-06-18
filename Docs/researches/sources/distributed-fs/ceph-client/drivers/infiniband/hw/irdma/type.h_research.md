# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/type.h

## Purpose
This is the central shared type and prototype header for the IRDMA low-level hardware driver. It defines debug categories, protocol/error enums, hardware stats indexes, SC object layouts, QP/CQ/CEQ/AEQ/CQP/VSI/device state, offload context structures, CQP command payload unions, and SC-layer function prototypes.

## Important APIs, Types, And Functions
- Enumerations cover page sizes, terminate layers/errors, hardware statistics, firmware features, scheduling priority, VF/PF identity, HMC profiles, qhash entry/manage types, reserved CQ/QP ids, and queue types.
- Core runtime types include `struct irdma_hw`, `irdma_sc_dev`, `irdma_sc_vsi`, `irdma_sc_cqp`, `irdma_sc_qp`, `irdma_sc_cq`, `irdma_sc_srq`, `irdma_sc_ceq`, `irdma_sc_aeq`, `irdma_sc_pd`, and `irdma_pfpdu`.
- Offload and context types include TCP, UDP, RoCE, iWARP, QP host context, AEQE, MR/STag, qhash, ARP, APBVT, push-page, stats, QoS, and work-scheduler payloads.
- `union cqp_info` inside `struct cqp_info` models the parameter set for each CQP operation, and `struct cqp_cmds_info` is the queued command wrapper.
- Prototypes expose SC operations for CCQ/CEQ/AEQ/CQP/QP/CQ/SRQ lifecycle, QP modify/flush, fast register, static HMC pages, stats updates, and queue context setup.
- `irdma_sc_cqp_get_next_send_wqe()` is an inline wrapper around the indexed CQP WQE allocator.

## Control Flow
The header does not execute logic beyond the inline CQP WQE wrapper, but it defines the control contracts used by the driver. Initialization code fills `irdma_device_init_info`, `irdma_cqp_init_info`, `irdma_vsi_init_info`, and queue init info structs. CQP producers fill a `cqp_cmds_info` union arm, queue or post it, and CQP completion handling uses `irdma_ccq_cqe_info`. QP/CQ creation uses host context info and UK init substructures, then lower functions emit hardware WQEs using the fields defined here.

## State And Persistence
All structures describe in-memory kernel and hardware-facing state. `irdma_sc_dev` persists for device lifetime and owns MMIO doorbells, feature registers, HMC/FPM buffers, CQP/AEQ/CEQ/CCQ pointers, PUDA CQ pointers, QoS/work-scheduler state, virtual channel state, and locks. `irdma_sc_vsi` persists per virtual station interface and owns ILQ/IEQ resources, QoS mappings, MTU, stats, and callbacks. `irdma_sc_qp` and `irdma_sc_cq` persist per queue object and embed UK-level rings plus hardware addresses. `irdma_pfpdu` persists per QP for IEQ partial-FPDU processing.

## Dependencies And Integration Points
The header includes `osdep.h`, `irdma.h`, `user.h`, `hmc.h`, `uda.h`, `ws.h`, and `virtchnl.h`. It is consumed by most IRDMA implementation files and bridges Linux RDMA core objects to hardware command formats. It also integrates PUDA by storing `ilq`, `ieq`, `ilq_cq`, and `ieq_cq` pointers in VSI/device structs.

## Risks And Edge Cases
Because this file centralizes shared structure layout, small field changes can break many hardware WQE/context writers. Bitfield state such as `ceq_valid`, `stats_idx_valid`, `flush_sq/rq`, `virtual_map`, and offload-valid flags must match hardware command construction. Stats indexes vary by hardware generation. The CQP union requires callers and command dispatchers to agree exactly on `cqp_cmd`. Some fields are protected by specific locks or mutexes noted in comments, and misuse can cause races in QoS, CQP queues, virtual channel messaging, or PUDA CQ pointers.

## Test Signals
Full driver build coverage is the first signal. Runtime validation should cover device init/teardown, VSI creation, CQP command submission/completion, QP/CQ/SRQ lifecycle, stats gather, QoS/work-scheduler changes, virtual channel paths, IEQ partial mode, and sparse/pahole-style layout checks when hardware context code changes.
