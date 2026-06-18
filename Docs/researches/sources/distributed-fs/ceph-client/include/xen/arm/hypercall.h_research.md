<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h

## Purpose
This ARM Xen header declares Linux hypercall entry points and small wrappers for platform and suspend operations.

## Important APIs, Types, And Functions
- `privcmd_call()` exposes a generic privileged hypercall path with five arguments.
- `HYPERVISOR_*` declarations cover version, console I/O, grant table, scheduler, event channel, HVM, memory, physdev, vcpu, vm assist, device-model, platform, and multicall operations.
- `HYPERVISOR_platform_op()` sets `interface_version` before calling `HYPERVISOR_platform_op_raw()`.
- `HYPERVISOR_suspend()` builds a `sched_shutdown` with `SHUTDOWN_suspend` and invokes `SCHEDOP_shutdown`; `start_info_mfn` is unused on ARM.

## Control Flow
Callers construct Xen public ABI structures, pass them through the declared hypercall functions, and check negative return codes. Suspend flow is a scheduler shutdown request rather than a platform-specific CPU-state save.

## State And Persistence
No state is stored here. Hypercalls mutate Xen-managed domain state, event channels, grants, memory maps, scheduling state, or platform state depending on command.

## Dependencies And Integration Points
It depends on Xen public `xen.h`, `sched.h`, `platform.h`, Linux bug handling, and ARM hypercall implementation code. It is consumed by Xen event, grant, memory, HVM, and console subsystems.

## Risks And Edge Cases
Incorrect ABI structures or counts can corrupt hypercall results. `HYPERVISOR_platform_op()` must set the correct interface version. ARM suspend intentionally ignores `start_info_mfn`, so shared code must not rely on x86 semantics.

## Test Signals
Signals include successful Xen version query, console I/O, event-channel operations, grant table operations, platform ops with version set, and suspend/resume behavior through `SCHEDOP_shutdown`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/hypercall.h -->
