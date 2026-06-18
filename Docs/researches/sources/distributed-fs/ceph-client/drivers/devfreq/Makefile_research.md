# sources/distributed-fs/ceph-client/drivers/devfreq/Makefile

Purpose: kbuild recipe for devfreq core, event framework, governors, and platform drivers.

Important APIs/types/functions: builds `devfreq.o`, `devfreq-event.o`, governor objects, platform driver objects (`exynos-bus.o`, `hisi_uncore_freq.o`, `imx-bus.o`, `imx8m-ddrc.o`, `mtk-cci-devfreq.o`, `rk3399_dmc.o`, `sun8i-a33-mbus.o`, `tegra30-devfreq.o`), and descends into `event/`.

Control flow and state: object inclusion follows Kconfig symbols and keeps core/event/governor/platform implementation separated.

Dependencies and integration: ties `drivers/devfreq/Kconfig` symbols to compiled objects and the devfreq event subdirectory.

Risks and test signals: missing object mapping causes enabled drivers/governors to be absent or unresolved. Test all relevant modular/built-in combinations, event framework builds, and platform driver symbol names after refactors.
