# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.h

## Purpose
Defines VF FDIR context/state structures and declares the VF Flow Director virtchnl API.

## Important APIs and Types
- `enum ice_fdir_ctx_stat` records READY, IRQ completion, or TIMEOUT.
- `struct ice_vf_fdir_ctx` stores the timer, virtchnl opcode, status, completion descriptor, valid flag, and associated rule configuration pointer.
- `struct ice_vf_fdir` stores per-flow/tunnel filter counts, profile entry counts, total count, hardware profile pointer table, IDR/list rule registry, spinlock, and IRQ/done contexts.
- Under `CONFIG_PCI_IOV`, exports add/delete, init/exit, IRQ handler, and context flush. Without SR-IOV, exports no-op IRQ and flush stubs.

## Control Flow and State
The structures support one in-flight FDIR request and one completed context per VF. `ctx_lock` protects context flags and handoff between IRQ/timer and service task.

## Dependencies and Integration Points
Forward-declares `ice_vf`, `ice_pf`, and `ice_vsi`; relies on Flow Director constants/types from included driver headers at call sites. Used in `struct ice_vf` and VF reset paths.

## Risks
The `conf` pointer is untyped `void *`, so implementation must maintain correct ownership and casting. Stubs under non-IOV cover only IRQ/flush, so add/delete/init/exit users must be SR-IOV-gated.

## Test Signals
Compile with SR-IOV on/off, validate spinlock/timer lifecycle, ensure context flags are cleared after IRQ, timeout, reset, and exit.
