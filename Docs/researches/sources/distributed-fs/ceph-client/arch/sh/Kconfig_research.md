<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/Kconfig

Purpose: This is the main SuperH architecture Kconfig. It defines the `SUPERH` architecture capabilities, CPU family/subtype choices, timer/clock settings, kernel features, boot options, bus support, and power-management menu inclusion.

Important APIs/types/functions: Key symbols include `SUPERH`, CPU families `CPU_SH2`, `CPU_SH2A`, `CPU_J2`, `CPU_SH3`, `CPU_SH4`, `CPU_SH4A`, `CPU_SH4AL_DSP`, `CPU_SHX2`, `CPU_SHX3`, `ARCH_SHMOBILE`, CPU subtype configs from SH7619/J2 through SHX3/SH772x/SH778x, `SH_PCLK_FREQ`, `SH_CLK_CPG_LEGACY`, `ARCH_SUPPORTS_KEXEC`, `SMP`, `NR_CPUS`, `GUSA`, `GUSA_RB`, `HW_PERF_EVENTS`, builtin DTB options, boot offsets, command-line policy, and `MAPLE`.

Control flow: Kconfig selection starts by declaring SuperH architectural feature support, then presents a processor subtype choice whose entries select CPU families, pinctrl, timers, FPU/DSP, sparsemem, NUMA, USB, and other capabilities. It sources memory-management, CPU, board, driver, cpufreq, kernel HZ, SH driver, power, and cpuidle Kconfigs. Later menus derive default clock rates, image/link offsets, kexec/crash support, SMP limits, user-space atomicity options, command-line behavior, and Dreamcast Maple bus support.

State and persistence: Kconfig state persists in `.config` and drives compiler flags, included source directories, generated headers, boot layout, and runtime feature availability. There is no direct runtime code in this file.

Dependencies and integration points: It integrates with `arch/sh/Makefile`, `arch/sh/boards/Kconfig`, MM/Kconfig, CPU-specific Kconfig, drivers, kernel power/cpufreq/HZ menus, and generic kernel capability symbols.

Risks and test signals: Incorrect `select`/`depends on` relationships can create invalid board/CPU combinations or missing driver prerequisites. Defaults for clock frequency and boot offsets affect bootability on legacy boards. Tests include `make ARCH=sh olddefconfig` for representative board defconfigs, randconfig dependency checks, built-in DTB builds, SMP/J2/SHX3 configs, no-MMU configs, and boot smoke tests on emulators or hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/Kconfig -->
