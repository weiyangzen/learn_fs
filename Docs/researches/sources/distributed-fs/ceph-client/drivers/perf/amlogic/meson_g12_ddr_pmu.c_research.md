# sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_g12_ddr_pmu.c

Purpose: Implements the Amlogic G12A/G12B/SM1 DDR monitor hardware callbacks and platform driver glue for the generic Meson DDR PMU core.

Important APIs and functions: `dmc_g12_counter_enable()` programs a 100 ms timer from DDR PLL frequency and enables all four channels. `dmc_g12_counter_disable()` clears control, timer, counters, and port filters. `dmc_g12_set_axi_filter()`/`dmc_g12_config_fiter()` program major/subport filter registers per channel. `dmc_g12_get_counters()` reads total request/grant and per-channel grant counts. `dmc_g12_irq_handler()` detects and clears QOS timer IRQ. `g12a_dmc_info`, `g12b_dmc_info`, and `sm1_dmc_info` define capabilities and callbacks.

Control flow: OF matching selects a hardware-info structure, and probe delegates to `meson_ddr_pmu_create()`. During perf start, the core invokes `enable`; the G12 code calculates timer ticks from PLL registers, writes the timer, and sets enable/use-timer/channel bits. AXI filters are set before start based on perf event config bitmaps. On interrupt, the core invokes `irq_handler`, which reads counters if `DMC_QOS_IRQ` is set and writes back the control value to clear flags.

State and persistence: Hardware state lives in DMC monitor control registers, filter registers, timer, and counter registers. Capability bitmasks differ by SoC and control visible format attributes. The PLL register is read on each enable for current DDR frequency.

Dependencies and integration points: Depends on the generic Meson DDR PMU core and `soc/amlogic/meson_ddr_pmu.h`. Platform matching supports `amlogic,g12a-ddr-pmu`, `amlogic,g12b-ddr-pmu`, and `amlogic,sm1-ddr-pmu`.

Risks: Function name `dmc_g12_config_fiter` is misspelled but internal. `dmc_g12_set_axi_filter()` checks `channel > chann_nr`; an equal channel would pass, though current callers derive valid zero-based channels. Timer calculation depends on PLL encoding and defaults; bad PLL values can produce zero/invalid periods. Filter register programming treats ports >=32 as subports behind the device selector, so capability masks must match SoC wiring.

Test signals: Probe each compatible, sysfs format visibility differences for G12A/G12B/SM1, DDR bandwidth events over timer interrupts, PLL-derived timer sanity, per-channel filters for major and subport IDs, and clearing/re-enabling after stop/start cycles.
