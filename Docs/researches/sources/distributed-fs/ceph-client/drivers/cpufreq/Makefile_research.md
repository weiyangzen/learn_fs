# sources/distributed-fs/ceph-client/drivers/cpufreq/Makefile

Purpose: cpufreq build manifest mapping Kconfig symbols to core, governor, trace, x86, ARM, PowerPC, and miscellaneous platform driver objects.

Important APIs/types/functions: builds `cpufreq.o` and `freq_table.o` for `CONFIG_CPU_FREQ`, stats and governor objects for their symbols, generic DT/virtual objects, `amd_pstate-y := amd-pstate.o amd-pstate-trace.o`, x86 object ordering, ARM SoC driver mappings including `airoha-cpufreq.o`, and other architecture driver objects.

Control flow: Kbuild expands `obj-$(CONFIG_...)` entries based on `.config`; composite `amd_pstate-y` links the trace object into the AMD pstate module. Per-object `CFLAGS_amd-pstate-trace.o := -I$(src)` and `CFLAGS_powernv-cpufreq.o := -I$(src)` make local trace headers visible.

State and persistence: no runtime state; controls build outputs and module composition. Link order comments document precedence among x86 drivers.

Dependencies and integration: depends on Kbuild, Kconfig symbols from `drivers/cpufreq/Kconfig*`, and source files in the cpufreq directory. It integrates tracepoint generation by compiling `amd-pstate-trace.c`.

Risks: missing object entries make Kconfig options unbuildable. Link order matters for legacy x86 driver preference. Composite module definitions must include trace object exactly once to avoid missing or duplicate tracepoint definitions.

Test signals: `make drivers/cpufreq/` for representative configs, `modpost` for composite modules, verifying enabled Kconfig symbols produce expected `.o` or modules, and x86 build tests for ACPI/AMD pstate interactions.
