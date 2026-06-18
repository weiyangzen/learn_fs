<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h

Purpose: centralizes miscellaneous x86 architecture prototypes used by entry, syscall, NX setup, reboot, and 64-bit arch-prctl code. Important APIs include `syscall_init()`, entry symbols for native and compat syscall/sysenter/sysret paths, `x86_configure_nx()`, `reboot_force`, and `do_arch_prctl_64()`.

Control flow: initialization code calls `syscall_init()` and NX setup; ptrace and arch-prctl code call `do_arch_prctl_64()` for FS/GS and related 64-bit controls; entry code and helpers use the declared symbol boundaries for syscall-gap detection and single-step regions. Compat symbols are replaced with NULL when IA32 emulation is absent.

State and persistence: only declares runtime entry symbols and reboot flag state. Dependencies are LDT/task structures and architecture entry assembly. Risks are prototype mismatches with assembly, incorrect compat NULL assumptions, and syscall-gap boundary drift. Test signals include syscall/sysenter/sysret on native and compat tasks, NX boot configuration, and arch-prctl FS/GS tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/proto.h -->
