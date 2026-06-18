# sources/distributed-fs/ceph-client/drivers/firmware/tegra/Kconfig

Kconfig menu for Tegra firmware support. It defines `TEGRA_IVC`, the Inter-VM Communication protocol library, and `TEGRA_BPMP`, the Boot and Power Management Processor firmware driver.

`TEGRA_IVC` is a bool visible under `COMPILE_TEST` and depends on `ARCH_TEGRA`. `TEGRA_BPMP` depends on `ARCH_TEGRA`, `TEGRA_HSP_MBOX`, and little-endian CPU support, and selects `TEGRA_IVC`. The help text identifies BPMP as the firmware processor handling clocks, DVFS, thermal, and power management through HSP notifications plus IVC transport.

Integration is entirely build-time: these symbols control compilation of `ivc.o`, `tegra-bpmp.o`, and SoC-specific BPMP implementations through the sibling Makefile. Risks are mostly configuration coverage: `TEGRA_BPMP` is unavailable on big-endian builds and requires HSP mailbox support, so dependent clock/reset/power-domain consumers must tolerate probe deferral or missing BPMP. Test signals include randconfig coverage for `COMPILE_TEST`, dependency resolution on each Tegra SoC, and build checks that `select TEGRA_IVC` supplies transport symbols.
