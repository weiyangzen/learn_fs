<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kconfig -->
# sources/distributed-fs/ceph-client/arch/um/Kconfig

Purpose: defines the top-level User-Mode Linux architecture configuration menu. It declares UML as the active architecture, selects generic kernel capabilities, exposes UML-specific memory, SMP, static-linking, hostfs, management-console, SysRq, stack, page-table, time-travel, KASAN-shadow, suspend, and power-management options, and includes subarchitecture and driver Kconfig fragments.

Important APIs/types/functions: this is Kconfig metadata rather than C code. Important symbols are `UML`, `MMU`, `UML_DMA_EMULATION`, `NO_IOMEM`, `UML_IOMEM_EMULATION`, `STATIC_LINK`, `LD_SCRIPT_*`, `HOSTFS`, `MCONSOLE`, `MAGIC_SYSRQ`, `KERNEL_STACK_ORDER`, `UML_TIME_TRAVEL_SUPPORT`, `UML_MAX_USERSPACE_ITERATIONS`, and `KASAN_SHADOW_OFFSET`.

Control flow: Kconfig evaluation starts by enabling `UML` and its selected generic features, imports `arch/$(HEADER_ARCH)/um/Kconfig`, then exposes user-visible options. The file finally sources `arch/um/drivers/Kconfig`, marks suspend possible when not SMP, and includes `kernel/power/Kconfig`.

State and persistence: selected symbols persist in `.config` and generated autoconf headers. They control compile-time inclusion of drivers, memory emulation, link mode, time-travel hooks, and exported kernel features, but no runtime state is stored here.

Dependencies and integration points: integrates with arch-specific `HEADER_ARCH` Kconfig, generic TTY, procfs, power management, KASAN, LTO, Rust, syscall tracing, seccomp, hostfs, and UML drivers. `MCONSOLE` gates management console code; `UML_TIME_TRAVEL_SUPPORT` affects channels and RTC behavior; `STATIC_LINK` affects Makefile link flags and KASAN choices.

Risks: Kconfig selects are architectural ABI and build-contract knobs. Incorrect `select` or dependency changes can silently enable generic code UML cannot support. Time-travel is deliberately incompatible with SMP; static linking can conflict with runtime-loaded host dependencies; `NO_DMA` must stay disabled when UML DMA emulation is required.

Test signals: all relevant defconfigs should resolve without dependency warnings, UML should build both 32-bit and 64-bit where supported, static/dynamic link variants should link, `mconsole`/hostfs/time-travel options should include or exclude expected objects, and `make olddefconfig` should keep stable defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/Kconfig -->
