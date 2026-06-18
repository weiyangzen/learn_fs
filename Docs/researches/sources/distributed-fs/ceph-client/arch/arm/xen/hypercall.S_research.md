## sources/distributed-fs/ceph-client/arch/arm/xen/hypercall.S

### Purpose
Implements ARM Xen hypercall wrappers using the Xen-specific HVC immediate and ARM register calling convention.

### Important APIs, Types, And Functions
Exports wrappers such as `HYPERVISOR_xen_version`, `console_io`, `grant_table_op`, `sched_op`, `event_channel_op`, `hvm_op`, `memory_op`, `physdev_op`, `vcpu_op`, `platform_op_raw`, `multicall`, `vm_assist`, `dm_op`, and `privcmd_call`.

### Control Flow
Wrapper macros move the hypercall number into `r12`, issue `HVC #0xEA1`, and return with result in `r0`. Five-argument calls save/load `r4` for the fifth argument. `privcmd_call` remaps user-provided arguments into hypercall registers, temporarily enables kernel user access around the HVC, then disables it.

### State, Persistence, And Dependencies
No persistent storage. Depends on Xen hypercall numbers, `__HVC`, ARM ABI, and uaccess enable/disable assembler macros.

### Integration Points
Called by ARM Xen C code and exported for generic Xen subsystems and privcmd userspace forwarding.

### Risks
Register save/restore bugs corrupt callers. `privcmd_call` must bracket user memory access exactly or create security exposure. Hypercall immediate must remain Xen's ARM tag.

### Test Signals
Boot Xen guests, run grant/event/memory hypercall paths, exercise `/dev/xen/privcmd`, and inspect disassembly for register convention correctness.
