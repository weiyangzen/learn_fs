# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.h

## Purpose
`qed_hw.h` declares the public internal interface for QED hardware access. It exposes opaque PTT handling, BAR/GRC accessors, pretend operations, DMAE utilities, firmware data initialization, queue-manager PQ parameter shapes, and hardware error notification.

## Important APIs, Types, and Functions
- `enum reserved_ptts` defines reserved PTT slots for engineering diagnostics, user space, main, and DPC use.
- DMAE command constants define go value, completion value, command size, minimum wait time, and max clients.
- PTT APIs include pool allocation/free, window address accessors, window retargeting, reserved PTT lookup, and raw read/write/copy helpers.
- Pretend APIs switch access identity for function and/or port.
- `union qed_qm_pq_params` supplies protocol-specific PQ parameter variants for iSCSI, core, Ethernet, and RoCE.
- DMAE APIs allocate/free DMAE info, map DMAE indices to go commands, run a sanity copy, and initialize firmware data.
- `qed_hw_err_notify()` is marked cold and printf-checked.

## Control Flow
The header is consumed by most QED modules that need a PTT and low-level hardware access. Typical call flow is acquire or retrieve a PTT, issue `qed_rd/qed_wr` or DMAE operations, and then release the PTT if dynamically acquired.

## State and Persistence
The header declares interfaces that mutate `struct qed_hwfn` state, PTT window hardware state, DMAE coherent buffers, and management firmware error state. The opaque `struct qed_ptt` prevents most callers from depending on the concrete PTT layout.

## Dependencies and Integration Points
It includes Linux type/bit/slab/string headers and QED core device definitions. `qed_init_ops.c`, `qed_init_fw_funcs.c`, `qed_int.c`, `qed_iscsi.c`, and many other driver files use these declarations for register access, runtime init flushing, CAU/IGU programming, statistics reads, and storage offload ramrods.

## Risks
- The API is low-level and assumes callers use the correct PTT context and locking.
- Function comments contain a few stale return descriptions, so implementation should be treated as authoritative.
- DMAE address-type expectations are not encoded in the function prototypes, leaving room for caller-side unit mistakes around bytes versus dwords.

## Test Signals
Compile coverage is important because this header binds many modules. Runtime signals include successful PTT allocation, DMAE sanity checks, and callers being able to gather stats or initialize runtime registers without GRC/DMAE errors.
