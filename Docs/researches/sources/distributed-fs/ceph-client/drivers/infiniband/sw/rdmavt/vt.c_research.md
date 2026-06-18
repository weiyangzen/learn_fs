# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/vt.c

## Purpose
`vt.c` is the rdmavt library registration and RDMA core operations file. It allocates/deallocates rdmavt-backed IB devices, installs common `ib_device_ops`, validates provider hook coverage, initializes common rdmavt subsystems, registers/unregisters devices with the IB core, and initializes per-port state.

## Important APIs, types, and functions
Module init/exit call `rvt_driver_cq_init()` and `rvt_cq_exit()`. Exported APIs include `rvt_alloc_device()`, `rvt_dealloc_device()`, `rvt_register_device()`, `rvt_unregister_device()`, and `rvt_init_port()`. Static verbs handlers cover query/modify device/port, pkey/gid queries, ucontext allocation/deallocation, immutable port data, and `rvt_dev_ops` binding for AH, CQ, PD, MR, QP, SRQ, mmap, and multicast operations.

## Control flow
Provider drivers allocate an rdmavt device, fill `rdi->dparms`, ports, and `driver_f` hooks, then call `rvt_register_device()`. Registration first validates hook support for each rdmavt-managed verb through `check_support()`, installs common IB ops, initializes mmap, QP, AH count, SRQ, multicast, MR, WSS, CQ and PD state, updates user verbs command masks and device defaults, registers the IB device, and creates MAD agents. Failure unwinds WSS, MR, and QP state. Unregistration frees MAD agents, unregisters the IB device, and tears down WSS, MR, and QP state.

## State and persistence
State is per `struct rvt_dev_info`: port pointer array, device attributes, operation tables, counters, subsystem allocation tables, pkey tables, capability flags, and provider callbacks. It is in-memory only and persists until provider unregister.

## Dependencies and integration points
The file integrates rdmavt with RDMA core `ib_device_ops`, provider-specific `driver_f` hooks, MAD agent support, mmap/CQ/MR/QP/SRQ/AH/mcast modules, PCI-backed logging macros, and optional provider ucontext hooks.

## Risks
`check_support()` is the guardrail that prevents rdmavt from installing verbs without provider support; incomplete checks can produce runtime null calls. Registration unwind must match initialization order. `rvt_modify_device()` returns unsupported unless a provider overrides it, so feature additions must decide where responsibility belongs. Query functions assume provider-maintained port and pkey data are current.

## Test signals
Build and load an rdmavt provider, verify registration failure for missing hooks, exercise every installed verbs op, confirm uverbs ABI version and command masks, test port query/modify/pkey/gid behavior, and run unload tests under active object teardown to catch subsystem leaks.
