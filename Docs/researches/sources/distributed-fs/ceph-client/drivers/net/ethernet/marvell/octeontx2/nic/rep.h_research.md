# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.h

## Purpose
`rep.h` declares the RVU representor driver's public types, PCI device ID, and lifecycle/event APIs.

## Important APIs, Types, and Definitions
It defines `PCI_DEVID_RVU_REP`, `struct rep_stats`, `struct rep_dev`, flag `RVU_REP_VF_INITIALIZED`, inline `otx2_rep_dev()`, and prototypes for `rvu_rep_create()`, `rvu_rep_destroy()`, and `rvu_event_up_notify()`.

## Control Flow
The only executable logic is `otx2_rep_dev()`, which identifies representor PCI devices by device ID. The prototypes connect common PF/devlink code and mailbox event handlers to `rep.c`.

## State and Persistence
`rep_dev` persists per representor netdev and tracks master device linkage, devlink port, flow configuration, stats work, VF init state, pcifunc, rep ID, and MAC. `rep_stats` stores cached counters and an atomic discard counter.

## Dependencies and Integration Points
The header includes PCI, RVU register, TX/RX, and common driver headers. It is consumed by `rep.c` and TC code that needs `struct rep_dev` for redirect/representor handling.

## Risks and Edge Cases
`OTX2_MAX_CQ_CNT` bounds representor count via queue capacity. The header exposes internals used across modules, so field changes can affect TC redirect and stats paths. `flow_cfg` ownership/lifetime must be clear because representor TC allocates it lazily.

## Test Signals
Compile representor-enabled builds, verify PCI ID matching, create maximum representor counts, and exercise TC redirect paths that cast target netdev private data to `rep_dev`.
