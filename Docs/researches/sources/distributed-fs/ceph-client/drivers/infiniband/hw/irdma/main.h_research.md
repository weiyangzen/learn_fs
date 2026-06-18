# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.h

## Purpose
`main.h` is the central private header for the IRDMA Linux driver. It gathers Linux/RDMA includes, shared constants, initialization state enums, control queue structures, interrupt/event queue wrappers, resource tracking, generation callbacks, primary device structures, inline conversion helpers, resource bitmap helpers, and cross-file prototypes.

## Important APIs, types, and functions
Important types are `enum init_completion_state`, `struct irdma_cqp_request`, `struct irdma_cqp`, `struct irdma_ccq`, `struct irdma_ceq`, `struct irdma_aeq`, `struct irdma_pci_f`, `struct irdma_device`, and `struct irdma_gen_ops`. Inline helpers include `to_iwdev`, `to_iwqp`, `dev_to_rf`, `irdma_alloc_rsrc`, and `irdma_free_rsrc`. It prototypes major control/runtime APIs, CQP operations, CM helpers, qhash/APBVT/ARP operations, and notifier callbacks.

## Control flow, state, and persistence
The header defines the state machine used by `hw.c` for staged initialization and teardown. `struct irdma_pci_f` persists control-plane hardware state, resource bitmaps, HMC/PBLE data, queue objects, MSI-X tables, workqueues, generation ops, and locks. `struct irdma_device` persists the IB-facing runtime object, netdev, VSI, CM core, RoCE/iWARP mode flags, and runtime init state.

## Dependencies and integration points
It includes kernel networking, PCI, DMA, workqueue, auxiliary bus, RDMA core, ABI, and local IRDMA headers. Almost every file in this subset depends on it for shared contracts, especially `hw.c`, generation interface files, verbs, CM, PBLE, and HMC code.

## Risks and test signals
Risks are global coupling, stale prototypes, lock-order assumptions, resource bitmap off-by-one behavior, and init-state mismatch. Tests should cover resource allocation wraparound, init/deinit state transitions, compile coverage across feature configs, and lifetime checks for `rf` versus `iwdev` in Gen3 core/vport mode.
