
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.h

## Purpose
Provides the compile-time interface for PowerPC KVM exit timing and always-on lightweight exit accounting. When timing is disabled, it supplies no-op stubs while preserving call sites.

## Important APIs, Types, And Functions
Declares or defines `kvmppc_init_timing_stats()`, `kvmppc_update_timing_stats()`, `kvmppc_create_vcpu_debugfs_e500()`, `kvmppc_set_exit_type()`, `kvmppc_account_exit_stat()`, and `kvmppc_account_exit()`. `kvmppc_account_exit_stat()` increments `vcpu->stat` fields for constants such as `MMIO_EXITS`, `DEC_EXITS`, `EXT_INTR_EXITS`, TLB miss exits, doorbells, and emulated instruction exits.

## Control Flow
With `CONFIG_KVM_EXIT_TIMING`, callers set `last_exit_type` and timing.c records durations. Without it, timing calls compile away. `kvmppc_account_exit()` always sets the timing type if available and increments the matching statistics field through a switch that requires the type to be a compile-time constant.

## State And Persistence
This header updates only vCPU stat and optional timing fields. It does not allocate state.

## Dependencies And Integration Points
Included by common emulation, MMU, e500mc, and timing implementation files. It depends on `linux/kvm_host.h` and exit-type/stat definitions in the PowerPC KVM arch structures.

## Risks
The `BUILD_BUG_ON(!__builtin_constant_p(type))` requirement prevents dynamic exit-type accounting through this helper. Missing switch cases silently produce no stat increment for new exit types unless the helper is updated. Stub behavior must stay signature-compatible with timing.c.

## Test Signals
Build coverage under both `CONFIG_KVM_EXIT_TIMING=y` and disabled configurations is the main signal. Runtime stats should increment for common exits even when timing debugfs is not built.
