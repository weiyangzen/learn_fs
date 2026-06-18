# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mmdc.c

Purpose: i.MX MMDC memory-controller support with optional perf PMU exposure. It records DDR type, enables automatic MMDC power saving, and registers fixed-function memory-controller counters for i.MX6Q/i.MX6QP.

Important APIs/types/functions: `imx_mmdc_get_ddr_type()`, `imx_mmdc_probe()`, `imx_mmdc_perf_init()`, `mmdc_pmu_event_init/add/del/start/stop/read()`, `mmdc_pmu_timer_handler()`, `mmdc_pmu_offline_cpu()`, `struct mmdc_pmu`, `struct fsl_mmdc_devtype_data`, PMU event/format/cpumask sysfs attributes, and the `imx-mmdc` platform driver.

Control flow: Probe enables the optional IPG clock, maps the MMDC register block from DT, reads `MMDC_MDMISC` into global `ddr_type`, clears the `MMDC_MAPSR` power-saving disable bit, then initializes the perf PMU if `CONFIG_PERF_EVENTS` is enabled. Perf events are fixed to six hardware counters, reject sampling/per-task use, pin to one CPU, program optional AXI ID filtering, poll every second with an hrtimer because no counter interrupt exists, and migrate context on CPU hotplug.

State and persistence: Persistent hardware state is MMDC register configuration: power-saving enable, profile control, AXI ID selector, and live 32-bit counter values. Kernel process state includes global `ddr_type`, the `mmdc_ida` id allocator, cpuhp state, per-PMU active event slots, hrtimer, selected CPU mask, mapped MMDC base, and enabled clock. Remove unregisters PMU/cpuhp state, unmaps MMDC, disables the clock, and frees memory.

Dependencies and integration points: Depends on platform device/OF matching (`fsl,imx6q-mmdc`, `fsl,imx6qp-mmdc`), Linux perf PMU core, hrtimers, CPU hotplug, clocks, MMIO helpers, and i.MX PM code that consumes `imx_mmdc_get_ddr_type()` for suspend DDR handling.

Risks: `of_iomap()` is only `WARN_ON` checked before dereference, so malformed DT can crash. The module parameter name is `pmu_pmu_poll_period_us`, which appears accidental but is ABI once exposed. Concurrent events share one profile-control register, so group validation and add ordering are critical. The PMU relies on polling before 32-bit overflow and assumes counter wrap within the selected period. Error unwinding leaves the global cpuhp state installed once created.

Test signals: Build with and without `CONFIG_PERF_EVENTS`, boot on i.MX6Q/QP DT, verify `/sys/bus/event_source/devices/mmdc*/events`, run `perf stat -e mmdc0/total-cycles/`, offline the bound CPU, and suspend/resume to check DDR type remains available.
