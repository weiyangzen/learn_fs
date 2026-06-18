# sources/distributed-fs/ceph-client/drivers/perf/amlogic/Kconfig

Purpose: Defines the Amlogic DDR bandwidth performance monitor config option.

Important APIs and entries: `MESON_DDR_PMU` is a tristate option titled "Amlogic DDR Bandwidth Performance Monitor" and depends on `ARCH_MESON || COMPILE_TEST`.

Control flow: When enabled, the parent Makefile descends into `drivers/perf/amlogic/` and builds the Meson DDR PMU composite object.

State and persistence: The option persists in kernel `.config` and controls module/built-in availability.

Dependencies and integration points: Sourced by `drivers/perf/Kconfig`; paired with `drivers/perf/amlogic/Makefile` and the G12 platform driver.

Risks: Too broad dependencies could build code without required SoC headers; too narrow dependencies reduce compile-test coverage. Help text promises multiple-channel bandwidth monitoring and should stay aligned with supported hardware data.

Test signals: Menu visibility under Meson and COMPILE_TEST, built-in/module builds, and object inclusion through the parent Makefile.
