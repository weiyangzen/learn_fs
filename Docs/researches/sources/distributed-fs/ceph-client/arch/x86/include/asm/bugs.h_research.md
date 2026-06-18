
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bugs.h

Purpose: x86 CPU bug handling declarations that need to be visible outside CPU initialization.

Important APIs and control flow: declares `ppro_with_ram_bug()` for 32-bit Intel builds and returns zero otherwise. Declares `cpu_bugs_smt_update()` for updating bug/mitigation state when SMT topology changes.

State, dependencies, and risks: state is CPU bug flags and mitigation state in CPU core code. Dependencies include processor structures and config-gated CPU vendors. Risks are stale bug state after SMT hotplug and build-specific behavior for old Pentium Pro errata. Test signals are CPU mitigation sysfs/status tests, SMT toggle tests, and 32-bit Intel build coverage.
