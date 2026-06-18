# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/microcode/internal.h

Purpose: defines the private interface shared by x86 microcode core and vendor implementations. It centralizes update result states, vendor callback shape, early-load revision reporting, CPUID vendor helpers that work before `boot_cpu_data` is ready, and build-time stubs for disabled Intel or AMD support.

Important APIs/types/functions: defines `enum ucode_state`, `struct microcode_ops`, `struct early_load_data`, `MAX_UCODE_COUNT`, CPUID vendor constants, `CPUID_IS()`, `x86_cpuid_vendor()`, and `x86_cpuid_family()`. It declares `early_data`, `ucode_cpu_info[]`, `microcode_rev[]`, `base_rev`, `hypervisor_present`, `force_minrev`, `find_microcode_in_initrd()`, AMD entry points, and Intel entry points. `ucode_dbg()` gates debug prints through `CONFIG_MICROCODE_DBG`.

Control flow: the inline CPUID helpers directly execute CPUID leaf 0 or 1 and return vendor/family before normal CPU structures are initialized. The rest is callback wiring: `core.c` calls `microcode_ops` methods and vendor-specific entry points through these declarations.

State and persistence: no state is owned here, but it declares shared runtime globals. It has no I/O or persistence behavior.

Dependencies and integration points: depends on `asm/cpu.h`, `asm/microcode.h`, early cpio/initrd definitions, `NR_CPUS`, and config symbols `CONFIG_CPU_SUP_AMD`, `CONFIG_CPU_SUP_INTEL`, and `CONFIG_MICROCODE_DBG`. It is the contract between `core.c`, `amd.c`, and `intel.c`.

Risks: `microcode_ops` semantics are synchronization-sensitive: core guarantees target-CPU execution for collection/apply/stage callbacks, and vendor code depends on that for MSR writes. Adding enum values or callback flags must keep `core.c` result handling in sync. CPUID vendor constants are byte-order-specific and must remain correct.

Test signals: builds with AMD-only, Intel-only, both, and neither vendor support; early boot before `boot_cpu_data`; debug and non-debug builds; and static analysis that every enabled vendor fills required callbacks.
