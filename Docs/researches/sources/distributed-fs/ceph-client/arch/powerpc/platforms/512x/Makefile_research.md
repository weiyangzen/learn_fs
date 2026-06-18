<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile

Purpose: maps MPC512x Kconfig symbols to the platform objects for shared setup, clock support, board files, CPLD support, LocalPlus FIFO, and PDM360NG.

Important APIs/types/functions: builds `clock-commonclk.o` when `COMMON_CLK` is enabled; always builds `mpc512x_shared.o`; conditionally builds `mpc5121_ads.o`, `mpc5121_ads_cpld.o`, `mpc512x_generic.o`, `mpc512x_lpbfifo.o`, and `pdm360ng.o`.

Control flow: make-time object selection follows Kconfig, determining which machine descriptors and platform devices enter the kernel.

State and persistence: build-time only.

Dependencies and integration: paired with `platforms/512x/Kconfig` and the Freescale platform source files not in this work item.

Risks and test signals: missing object mappings can make a selected board unbootable; common shared code is always linked for `PPC_MPC512x`. Test board-specific builds and module/builtin LPBFIFO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile -->
