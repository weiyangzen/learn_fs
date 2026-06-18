# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_ioctl.h

## Purpose
`cxgb3_ioctl.h` defines private ioctl command numbers and payload structures for `cxgb3` diagnostics and configuration through `SIOCCHIOCTL` (`SIOCDEVPRIVATE`).

## Important APIs, Types, And Functions
- Commands include MTU table get/set, PM get/set, memory read, firmware load, trace filter set, queue-set parameter get/set, and queue-set count get/set.
- `struct ch_reg`, `ch_cntxt`, `ch_desc`, and `ch_mem_range` describe register, context, descriptor, and memory-range access.
- `CNTXT_TYPE_EGRESS`, `CNTXT_TYPE_FL`, `CNTXT_TYPE_RSP`, and `CNTXT_TYPE_CQ` identify SGE context types.
- `struct ch_qset_params` mirrors queue sizes, interrupt latency, polling, LRO, congestion threshold, vector, and queue number.
- `struct ch_pktsched_params`, `ch_mtus`, `ch_pm`, `ch_tcam`, `ch_tcb`, `ch_tcam_word`, and `ch_trace` define scheduler, MTU, protocol-memory, TCAM/TCB, and trace-filter payloads.
- `TCB_WORDS` derives TCB array size from `TCB_SIZE`, and memory IDs are `MEM_CM`, `MEM_PMRX`, and `MEM_PMTX`.

## Control Flow And State
The header has no executable flow. User-space tooling passes these structures through the driver private ioctl handler. Handlers then read/write registers, contexts, descriptors, memory windows, firmware, queue-set parameters, MTU tables, protocol memory configuration, or trace filters.

## State And Persistence Behavior
Ioctls can read and mutate persistent adapter hardware state: firmware, MTU table, queue-set sizing/coalescing, protocol-memory parameters, trace filters, and hardware memory/register contents. The flexible array in `ch_mem_range` carries variable-length memory data. TCB/TCAM structures expose hardware connection/filter state.

## Dependencies And Integration Points
The header depends on fixed-width integer types, `NMTUS`, `TCB_SIZE`, and Linux private socket ioctl numbering. It integrates user-space diagnostics/configuration with T3 hardware management code and queue/offload internals.

## Risks And Edge Cases
Private ioctl structures are ABI-sensitive. Field size, alignment, and command number changes can break tools. Several payloads expose raw hardware memory/register access and firmware loading, so validation in handlers is critical. Variable-length memory ranges require careful copy bounds. Bitfields in `ch_trace` may be compiler-layout sensitive if shared directly with user space.

## Test Signals
Signals include ioctl ABI compile checks, user-tool compatibility, bounds checks for memory/register/context reads, firmware load success/failure paths, qset parameter round trips, MTU table round trips, and trace filter programming verified by captured traffic or hardware trace output.
