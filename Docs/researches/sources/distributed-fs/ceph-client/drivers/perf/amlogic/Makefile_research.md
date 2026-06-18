# sources/distributed-fs/ceph-client/drivers/perf/amlogic/Makefile

Purpose: Builds the Amlogic Meson DDR PMU driver as a composite object.

Important APIs and entries: `obj-$(CONFIG_MESON_DDR_PMU) += meson_ddr_pmu_g12.o` and `meson_ddr_pmu_g12-y := meson_ddr_pmu_core.o meson_g12_ddr_pmu.o`.

Control flow: Kbuild links the generic core and G12 hardware implementation into one module/object when `MESON_DDR_PMU` is enabled.

State and persistence: No runtime state; it defines build composition.

Dependencies and integration points: Requires exported non-static functions in `meson_ddr_pmu_core.c` to be visible to `meson_g12_ddr_pmu.c` within the composite object.

Risks: Adding a new SoC implementation requires updating the composite object or adding a new target; otherwise OF compatibles may exist without linked hardware callbacks.

Test signals: Module build, `meson_ddr_pmu_g12.ko` composition, and modpost resolving `meson_ddr_pmu_create()`/`remove()`.
