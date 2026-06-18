# sources/distributed-fs/ceph-client/drivers/perf/Makefile

Purpose: Maps performance monitor Kconfig symbols to built objects and subdirectories.

Important APIs and entries: Relevant entries include `obj-$(CONFIG_ARM_CCI_PMU) += arm-cci.o`, `obj-$(CONFIG_ARM_CCN) += arm-ccn.o`, `obj-$(CONFIG_APPLE_M1_CPU_PMU) += apple_m1_cpu_pmu.o`, `obj-$(CONFIG_ALIBABA_UNCORE_DRW_PMU) += alibaba_uncore_drw_pmu.o`, and `obj-$(CONFIG_MESON_DDR_PMU) += amlogic/`. It also routes Hisilicon and Arm CSPMU subdirectories and many other platform PMU objects.

Control flow: Kbuild evaluates `obj-y`/`obj-m` from configuration symbols and descends into subdirectories when enabled. Single-file drivers build directly; Amlogic builds through its own Makefile.

State and persistence: No runtime state. The file determines build graph state and module linkage.

Dependencies and integration points: Paired with `drivers/perf/Kconfig` and per-subdirectory Makefiles. Object names must match source filenames and module expectations.

Risks: Mismatched Kconfig symbol/object names silently omit drivers or break builds. Subdirectory entries depend on subdir Makefiles defining composite objects correctly.

Test signals: `make drivers/perf/`, all relevant `CONFIG_*` combinations as built-in and module, and module file names matching expected aliases.
