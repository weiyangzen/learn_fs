# subset-b-001189 clocksource driver research

This grouped report covers the requested Linux clocksource and clockevent drivers under `sources/distributed-fs/ceph-client/drivers/clocksource`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-sysost.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-sysost.c

Purpose: implements the Ingenic X1000 SYSOST timer block as both a small clock provider and a Linux time source. Channel 1 is used as a one-shot per-CPU-style clockevent, channel 2 is used as a 32-bit free-running clocksource and sched_clock source, and the file registers two child clocks, `percpu timer` and `global timer`, derived from the external parent clock.

Important APIs, types, and functions: `struct ingenic_ost`, `struct ingenic_ost_clk`, `struct ingenic_ost_clk_info`, and `struct ingenic_soc_info` hold the MMIO base, exported `clk_hw` objects, clockevent, clocksource, and SoC channel count. Clock operations are implemented by `ingenic_ost_*_recalc_rate()`, `ingenic_ost_determine_rate()`, and `ingenic_ost_*_set_rate()` using prescale fields in `OSTCCR`. Runtime timer paths are `ingenic_ost_cevt_set_next()`, `ingenic_ost_cevt_cb()`, `ingenic_ost_global_timer_read_cntl()`, `ingenic_ost_percpu_timer_init()`, `ingenic_ost_global_timer_init()`, and `ingenic_ost_init()`.

Control flow: `TIMER_OF_DECLARE()` calls `ingenic_ost_init()` for `"ingenic,x1000-ost"`. Probe maps the OST registers, enables the `"ost"` bus clock, registers the one-cell clock provider, stores the global `ingenic_ost` pointer, initializes the clocksource, initializes the one-shot clockevent IRQ, then registers sched_clock last because it cannot be undone. A next event clears the flag, writes `OST1DFR`, clears the counter, enables channel 1, and unmasks the interrupt; the ISR disables channel 1 and calls the clockevent handler.

State and persistence: state is all in MMIO registers, the static global pointer, the registered clocks, and the in-memory clockevent/clocksource structs. There is no disk persistence. Prescaler changes affect the hardware clock rates for both timer channels. Error unwind releases clocks and clocksource resources, but successful early timer registration is effectively permanent.

Dependencies and integration points: depends on OF address/IRQ parsing, common clock framework provider APIs, clocksource/clockevents, sched_clock, IRQ core, and dt-bindings `ingenic,sysost.h`. The child clocks are looked up through the provider itself via `of_clk_get_from_provider()`.

Risks: prescaler bit masks share `OSTCCR`, so rate changes for one channel must preserve the other channel. The driver assumes one SYSOST instance through the global `ingenic_ost`. IRQ lookup treats zero as invalid, so DT IRQ mapping must be correct. Sched_clock registration after global timer setup is intentionally last. Test signals include boot on X1000 DT, visible `ingenic-ost` clocksource, firing one-shot events, correct child clock rates, and clean logs for clock, IRQ, and registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-sysost.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-timer.c

Purpose: provides clocksource, sched_clock, and one-shot per-CPU clockevent support using the Ingenic TCU MFD/regmap block on JZ47xx and X1000 SoCs. It reserves non-PWM TCU channels for CPU timers and one extra channel for a 16-bit clocksource.

Important APIs, types, and functions: `struct ingenic_tcu` stores the regmap, OF node, clocksource clock/channel, PWM channel mask, and flexible array of `struct ingenic_tcu_timer`. The clocksource path uses `ingenic_tcu_timer_read()` and `ingenic_tcu_clocksource_init()`. Clockevent operations are `ingenic_tcu_cevt_set_state_shutdown()`, `ingenic_tcu_cevt_set_next()`, `ingenic_tcu_cevt_cb()`, and `ingenic_tcu_setup_cevt()`. Power management is handled by `ingenic_tcu_suspend()` and `ingenic_tcu_resume()`.

Control flow: early OF timer declaration clears `OF_POPULATED`, obtains the syscon regmap, allocates per-possible-CPU timers, computes a PWM-reserved mask from DT, chooses the first free channels for CPU events and the next free channel for the clocksource, registers the clocksource, installs a dynamic CPU hotplug state to set up clockevents, and finally registers sched_clock. On each CPU online path the driver obtains the channel clock from the TCU clock provider, enables it, maps a child IRQ through the TCU IRQ domain, requests an IRQ, and registers a one-shot clockevent. The IRQ disables the channel and uses `smp_call_function_single_async()` to run the target CPU event handler.

State and persistence: runtime state lives in TCU channel registers, regmap, enabled clocks, IRQ mappings, and the global `ingenic_tcu` pointer. The PWM mask is read once during init and controls channel ownership. Suspend disables the clocksource clock and all online CPU timer clocks in noirq phase; resume re-enables them.

Dependencies and integration points: integrates with `linux/mfd/ingenic-tcu.h`, syscon/regmap, the TCU clock provider, the TCU IRQ domain, clockevents, clocksource, sched_clock, CPU hotplug, and PM noirq callbacks.

Risks: channel allocation is sensitive to `ingenic,pwm-channels-mask` and `num_possible_cpus()`. Clockevents are 16-bit and reject deltas above `0xffff`. The interrupt path targets `timer->cpu` asynchronously, so CPU hotplug and call-single data reuse must stay consistent. Test signals include successful boot on each compatible, free TCU channels left for PWM, hotplug online timer setup, one-shot tick delivery, suspend/resume without lost clocks, and no invalid mask messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/jcore-pit.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/jcore-pit.c

Purpose: implements the J-Core programmable interval timer as a 32-bit MMIO clocksource, sched_clock provider, and per-CPU clockevent device. It also reads a seconds/nanoseconds pair from the PIT for stable high-level time reads.

Important APIs, types, and functions: `struct jcore_pit` contains a `clock_event_device`, per-CPU MMIO base, periodic delta, and precomputed enable word. `jcore_sched_clock_read()` reads `SECLO` and `NSEC` with retry against second rollover. `jcore_pit_set()`, `jcore_pit_disable()`, state callbacks, `jcore_timer_interrupt()`, `jcore_pit_local_init()`, and `jcore_pit_init()` are the main control paths.

Control flow: OF init maps the first PIT resource, parses the IRQ, registers the clocksource through `clocksource_mmio_init()` using `jcore_clocksource_read()`, registers sched_clock at `NSEC_PER_SEC`, allocates per-CPU PIT state, requests a percpu IRQ, computes the PIT enable register fields from the mapped hardware IRQ and priority bits, maps a PIT region for every present CPU, initializes each `clock_event_device`, and registers a CPU hotplug startup/teardown state. CPU startup derives frequency from `REG_BUSPD`, configures the device, and enables the percpu IRQ. The ISR disables the timer in oneshot mode and calls the event handler.

State and persistence: state is per-CPU allocated memory plus hardware throttle, enable, and bus-period registers. The IRQ programming value is static after init. There is no persistent state outside the kernel lifetime.

Dependencies and integration points: depends on OF address/IRQ parsing, percpu IRQs, CPU hotplug, `clocksource_mmio_init()`, sched_clock, and architecture IRQ mapping details exposed through `irq_get_irq_data()`.

Risks: the hardware IRQ encoding is unusual and mixes trap number and priority into the PIT enable word; interrupt-controller changes can break timer delivery. The driver maps one resource per present CPU and only logs if a CPU mapping is missing, so partial DT resources can leave CPUs without usable timer MMIO. Test signals include per-CPU hotplug tick setup, correct bus-period-derived rate, sched_clock monotonicity around second rollover, and no missing CPU PIT mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/jcore-pit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mips-gic-timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/mips-gic-timer.c

Purpose: registers the MIPS GIC counter as a clocksource and sched_clock source where safe, and exposes the GIC compare interrupt as a percpu one-shot clockevent.

Important APIs, types, and functions: global state includes per-CPU `gic_clockevent_device`, `gic_timer_irq`, `gic_frequency`, `gic_count_width`, and `gic_clock_unstable`. Counter reads are handled by `gic_read_count_2x32()`, `gic_read_count_64()`, and `gic_hpt_read_multicluster()`. Event and hotplug paths are `gic_next_event()`, `gic_compare_interrupt()`, `gic_clockevent_cpu_init()`, `gic_starting_cpu()`, and `gic_dying_cpu()`. Clock-rate changes are watched by `gic_clk_notifier()`.

Control flow: OF init verifies a real MIPS GIC parent, obtains frequency from a clock or `clock-frequency`, parses the timer IRQ, initializes the clocksource with a mask derived from GIC count-width config, and requests the percpu compare IRQ. CPU startup clears `GIC_CONFIG_COUNTSTOP`, registers the local clockevent, and enables the IRQ. `set_next_event` writes either the local virtual processor compare register or a remote VP compare register. The ISR acknowledges by rewriting compare and dispatches the event handler.

State and persistence: state is in GIC count/compare registers, per-CPU clockevent objects, the clock notifier, and the unstable flag. Frequency changes update clockevents on all CPUs and mark the clocksource unstable.

Dependencies and integration points: integrates with MIPS CPS/CM/GIC accessors, CPU hotplug, percpu IRQs, clock notifiers, clocksource, clockevents, and VDSO clock mode selection. Multicluster systems use redirected counter reads and disable VDSO mode.

Risks: using sched_clock is restricted to stable-frequency or CM3+ cases and non-multicluster systems. Remote compare programming depends on `mips_cm_vp_id(cpu)`. Clock-rate changes make the clocksource unstable, so cpufreq behavior is central. Test signals include clean DT parent validation, working percpu timer IRQs on hotplug, stable reads on 32-bit and 64-bit counters, correct behavior under cpufreq, and expected VDSO clock mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mips-gic-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/mmio.c

Purpose: provides a small reusable helper for registering simple MMIO-backed clocksources whose counter can be read directly from a 16- to 64-bit register.

Important APIs, types, and functions: `struct clocksource_mmio` wraps the target MMIO register and embedded `struct clocksource`. Exported-style helper functions are `clocksource_mmio_readl_up()`, `clocksource_mmio_readl_down()`, `clocksource_mmio_readw_up()`, and `clocksource_mmio_readw_down()`. `clocksource_mmio_init()` allocates the wrapper, validates bit width, fills clocksource fields, marks it continuous, and calls `clocksource_register_hz()`.

Control flow: clients call `clocksource_mmio_init(base, name, hz, rating, bits, read)`. The chosen read callback converts a 32-bit or 16-bit MMIO read into an increasing cycle value, either directly for up-counters or by inverting and masking down-counters. The helper does no mapping or clock enabling; callers must prepare hardware first.

State and persistence: only one allocated wrapper is created per call, and the state is owned by the clocksource core after successful registration. There is no cleanup on registration failure beyond normal allocation lifetime concerns visible in callers.

Dependencies and integration points: depends on `clocksource_register_hz()`, relaxed MMIO read accessors, and kernel allocation. It is used by many platform timer drivers in this group as their clocksource registration primitive.

Risks: callers must pass the actual readable counter register, a correct width, an accurate frequency, and a read function matching counter direction and access size. Passing `NULL` only works when the callback ignores the wrapper register, as EP93xx does. Bit widths below 16 or above 64 are rejected. Test signals are downstream: clocksource registration succeeds, `clocksource` debugfs shows the expected name/rating/mask, and monotonicity tests match the counter direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mps2-timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/mps2-timer.c

Purpose: supports ARM MPS2 timers as one free-running down-counting clocksource/sched_clock and one interrupt-driven clockevent. Multiple matching DT nodes are consumed one at a time: the first successful node becomes clocksource, and another becomes clockevent.

Important APIs, types, and functions: `struct clockevent_mps2` stores the register base, per-tick reload count, and clockevent. `mps2_sched_read()`, `mps2_timer_shutdown()`, `mps2_timer_set_next_event()`, `mps2_timer_set_periodic()`, `mps2_timer_interrupt()`, `mps2_clockevent_init()`, `mps2_clocksource_init()`, and `mps2_timer_init()` are the main routines.

Control flow: init first attempts `mps2_clocksource_init()`, using either `clock-frequency` or a DT clock. It maps registers, disables the timer, loads `0xffffffff` into value and reload, starts it, registers a down-counting MMIO clocksource, and registers sched_clock. Later matching calls initialize the clockevent by mapping a register block, parsing IRQ, allocating `clockevent_mps2`, disabling the timer, requesting the IRQ, and registering periodic plus one-shot clockevents. The ISR checks the interrupt status register, clears it, and invokes the event handler.

State and persistence: the static booleans `has_clocksource` and `has_clockevent` prevent duplicate registration. Clocksource base is stored in `sched_clock_base`; clockevent state is heap allocated and effectively permanent after early init. Hardware state is in control, value, reload, and interrupt registers.

Dependencies and integration points: uses OF clocks or `clock-frequency`, OF IRQ/address mapping, `clocksource_mmio_init()`, sched_clock, clockevents, and IRQF_TIMER handling.

Risks: DT must expose enough compatible timer instances because a single node cannot become both source and event in one call path. The clocksource and event timers may use separate clock resources, so mismatched rates are possible. The interrupt handler returns `IRQ_NONE` for a zero status, making spurious interrupts visible. Test signals include two MPS2 timer nodes registering both roles, monotonic down-count clocksource reads, periodic and one-shot event delivery, and no failed clock or IRQ messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mps2-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mxs_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/mxs_timer.c

Purpose: supports Freescale MXS TIMROT blocks on MX23 and MX28, using one timer for clockevents and another for clocksource. It handles the v1 16-bit hardware and v2 32-bit hardware differences.

Important APIs, types, and functions: static state includes `mxs_timrot_base`, `timrot_major_version`, and `mxs_clockevent_device`. Version-specific paths are `timrotv1_get_cycles()`, `timrotv1_set_next_event()`, and `timrotv2_set_next_event()`. Common paths include `timrot_irq_disable()`, `timrot_irq_enable()`, `timrot_irq_acknowledge()`, `mxs_irq_clear()`, `mxs_clockevent_init()`, `mxs_clocksource_init()`, and `mxs_timer_init()`.

Control flow: OF init maps the TIMROT block, obtains and enables the clock, resets the block with `stmp_reset_block()`, reads the major version from the appropriate offset, programs timer 0 as the event timer and timer 1 as the source timer, loads the source timer with max count, registers the clocksource, registers the clockevent, parses IRQ, and requests it with `IRQF_TIMER | IRQF_IRQPOLL`. The event IRQ acknowledges the timer interrupt and calls the clockevent handler.

State and persistence: runtime state is global and single-instance. Counter direction is down-counting, with inverted reads for clocksource. For v2, sched_clock is registered against the running count; v1 only registers a 16-bit clocksource. There is no dynamic cleanup after successful early registration.

Dependencies and integration points: depends on OF, clock framework, STMP reset helpers, `clocksource_mmio_init()`, clockevents, IRQ handling, and sched_clock for v2.

Risks: v1 and v2 use different register layouts and select values; wrong compatible/version offset breaks both source and event channels. `mxs_set_oneshot()` only clears IRQ state when already oneshot, so mode transitions rely on clockevent core ordering. Test signals include MX23 and MX28 boot coverage, correct counter width/range, no stale interrupt after shutdown, one-shot event delivery, and stable sched_clock on v2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/mxs_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/nomadik-mtu.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/nomadik-mtu.c

Purpose: configures the ST-Ericsson/Nomadik MTU block with timer 0 as a free-running down-counting clocksource/sched_clock/delay timer and timer 1 as a periodic or one-shot clockevent.

Important APIs, types, and functions: global state includes `mtu_base`, `clkevt_periodic`, `clk_prescale`, `nmdk_cycle`, and `mtu_delay_timer`. Main operations are `nomadik_read_sched_clock()`, `nmdk_clkevt_next()`, `nmdk_clkevt_reset()`, `nmdk_clkevt_shutdown()`, `nmdk_clksrc_reset()`, `nmdk_timer_interrupt()`, `nmdk_timer_init()`, and `nmdk_timer_of_init()`.

Control flow: OF init maps registers, obtains APB and timer clocks, parses the IRQ, and calls common init. Common init enables both clocks, chooses prescale 16 only for high input rates over 32 MHz, computes the periodic cycle count, starts timer 0 in free-running 32-bit mode, registers a down-count MMIO clocksource and sched_clock, requests timer 1 IRQ, configures the clockevent, and registers a current timer delay source. A next-event call unmasks timer 1, loads the value, and starts oneshot mode; the ISR clears timer 1 and calls the event handler.

State and persistence: state is mostly global and assumes one MTU instance. The `clkevt_periodic` flag drives resume/reset behavior. Hardware state is in MTU load/background-load/control/interrupt registers. No disk persistence exists.

Dependencies and integration points: uses OF clocks named `apb_pclk` and `timclk`, MMIO clocksource helpers, sched_clock, ARM delay timer registration, and Linux clockevent infrastructure.

Risks: rate and prescale selection directly affect timer range and resolution. Timer 1 supports both modes but resume synthesizes behavior based on `clkevt_periodic`, so state transitions must keep that flag correct. Test signals include stable clocksource reads, working delay timer calibration, one-shot and periodic ticks, suspend/resume reprogramming, and no missing clock or IRQ messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/nomadik-mtu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/numachip.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/numachip.c

Purpose: registers the Numascale NumaChip2 local CSR timer as an x86 64-bit clocksource and per-CPU one-shot clockevent.

Important APIs, types, and functions: per-CPU `numachip2_ced`, `numachip2_clocksource`, and `numachip2_clockevent` define the clocksource/event devices. `numachip2_timer_read()` reads `NUMACHIP2_TIMER_NOW`; `numachip2_set_next_event()` writes a relative deadline; `numachip_timer_interrupt()` dispatches the platform IPI callback; `numachip_timer_each()` configures each CPU; and `numachip_timer_init()` is the arch initcall.

Control flow: at `arch_initcall`, the driver exits unless `numachip_system == 2`. It resets the timer, registers a 1 GHz-equivalent clocksource with identity mult/shift, installs `x86_platform_ipi_callback`, and schedules `numachip_timer_each()` on every CPU. Each CPU configures the timer interrupt CSR with platform IPI vector and local APIC ID, copies the static clockevent template, sets cpumask, and registers the clockevent.

State and persistence: state lives in NumaChip local CSR registers and per-CPU `clock_event_device` structs. There is no suspend, remove, or persistent storage handling in this file.

Dependencies and integration points: tightly integrated with x86 APIC/IPI plumbing, NumaChip CSR accessors, `numachip_system`, and the clockevents/clocksource core.

Risks: the interrupt routing word encodes local APIC ID and `X86_PLATFORM_IPI_VECTOR`; mistakes break per-CPU event delivery. The clocksource uses fixed mult/shift and `NSEC_PER_SEC` registration, assuming hardware units match nanosecond ticks. Test signals include detection only on NumaChip2 systems, clocksource registration as `numachip2`, per-CPU clockevents registered on all CPUs, and timer IPIs invoking event handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/numachip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/renesas-ostm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/renesas-ostm.c

Purpose: supports Renesas OSTM channels. The first probed channel becomes a free-running 32-bit clocksource and sched_clock; later channels become periodic/one-shot clockevents.

Important APIs, types, and functions: the file uses `struct timer_of` for MMIO, clock, and IRQ resources. Important functions are `ostm_timer_stop()`, `ostm_init_clksrc()`, `ostm_init_sched_clock()`, `ostm_clock_event_next()`, `ostm_shutdown()`, `ostm_set_periodic()`, `ostm_set_oneshot()`, `ostm_timer_interrupt()`, `ostm_init_clkevt()`, and `ostm_init()`.

Control flow: OF timer declaration and the built-in platform driver both call `ostm_init()`. It allocates `timer_of`, deasserts an optional reset, selects flags for base/clock and optionally IRQ depending on whether `system_clock` is already set, initializes resources with `timer_of_init()`, and branches by first-vs-later channel. The clocksource path stops the timer, writes free-run mode, starts it, registers an up-counting MMIO clocksource, and stores the sched_clock base. The event path configures callbacks and registers the clockevent. In oneshot interrupts, the channel is stopped before dispatching the event handler.

State and persistence: `system_clock` is the global selector and sched_clock base, so probe order determines channel role. Reset control is deasserted at init and asserted on failure. Hardware counter, compare, enable, and mode registers hold runtime state.

Dependencies and integration points: depends on `timer-of.h`, OF/platform probing, reset control, clocksource MMIO helper, clockevents, sched_clock, and IRQ handling. It marks nodes populated after successful setup.

Risks: first-probed-channel semantics make DT ordering important. `ostm_timer_stop()` busy-waits for `TE` to clear, so hardware bus faults can hang early boot. Periodic compare uses `timer_of_period(to) - 1`. Test signals include one channel used for clocksource, second for events, reset deassert/assert behavior, periodic and oneshot ticks, and clean platform-driver reprobe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/renesas-ostm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/samsung_pwm_timer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/samsung_pwm_timer.c

Purpose: uses Samsung PWM timer channels as a clocksource, sched_clock, and clockevent provider for S3C/S5P-era SoCs. It chooses two PWM channels not reserved for external PWM outputs.

Important APIs, types, and functions: `struct samsung_pwm_clocksource` stores base, IRQs, variant data, chosen event/source channels, prescaler/divider values, and timer clock. Shared helpers include `samsung_timer_set_prescale()`, `samsung_timer_set_divisor()`, `samsung_time_stop()`, `samsung_time_setup()`, `samsung_time_start()`, `samsung_set_next_event()`, `samsung_set_periodic()`, `samsung_clock_event_isr()`, `samsung_clockevent_init()`, `samsung_clocksource_init()`, and `_samsung_pwm_clocksource_init()`. `samsung_pwm_lock` is exported for coordination with PWM users.

Control flow: DT init allocates variant data, parses IRQs and `samsung,pwm-outputs`, maps registers, obtains the `timers` clock, selects the highest-numbered non-output channel for source and the next for event, enables resources, registers the event device, then initializes the source timer and registers sched_clock/clocksource. Legacy board code can call `samsung_pwm_clocksource_init()` directly.

State and persistence: global `pwm` holds singleton state. Timer control registers are protected by `samsung_pwm_lock`. Suspend/resume callbacks stop or reprogram the source and event channels. There is no dynamic removal path for early timer setup.

Dependencies and integration points: integrates with OF timer declarations, common clock framework, clockevents, clocksource, sched_clock, Samsung PWM variant data, and the exported lock used by other Samsung PWM code.

Risks: channel selection must not conflict with output PWM channels. TCON bit layout has channel-specific gaps and channel 4 autoreload differences. `TINT_CSTAT` handling varies by variant. Test signals include correct source/event channel selection on each compatible, no PWM output conflicts, clocksource wrap behavior for 16-bit and 32-bit variants, interrupt clearing, and suspend/resume reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/samsung_pwm_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/scx200_hrt.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/scx200_hrt.c

Purpose: provides a high-resolution timer clocksource for the AMD/NSC SCx200 platform by exposing the chipset HRT counter to the Linux clocksource core.

Important APIs, types, and functions: module parameters `mhz27` and `ppm` select the 27 MHz clock mode and adjust the registered frequency. `read_hrt()` reads the 32-bit counter with `inl(scx200_cb_base + SCx200_TIMER_OFFSET)`. `cs_hrt` is the registered `struct clocksource`. `init_hrt_clocksource()` verifies the SCx200 configuration block, reserves the ISA I/O region, programs the timer configuration byte, computes frequency, and registers the clocksource.

Control flow: module initialization exits unless `scx200_cb_present()` reports the configuration block. It reserves the HRT I/O range with `request_region()`, writes `HR_TMEN` plus optional `HR_TMCLKSEL` to `SCx200_TMCNFG_OFFSET`, computes `HRT_FREQ + ppm` and multiplies by 27 in 27 MHz mode, logs the selected mode, and registers the continuous 32-bit clocksource. Reads return the current I/O counter value directly.

State and persistence: persistent state is limited to reserved I/O/MMIO resources and the registered clocksource object. The timer hardware itself continues counting independently; the driver does not store state to disk.

Dependencies and integration points: integrates with `linux/scx200.h`, the SCx200 configuration block base address, ISA I/O port reservation, Linux clocksource core, module initialization, and low-level `inl()`/`outb()` accessors. It is a platform-specific alternative to the bad TSC on older Geode-class hardware.

Risks: the main risks are hardware availability, exclusive I/O-region ownership, and correct frequency selection. `ppm` is added directly to the 1 MHz base before optional 27x multiplication, so parameter semantics matter. Counter width/frequency assumptions determine wrap handling and time conversion. Test signals include module load on SCx200 hardware, the clocksource appearing with the expected 1 MHz or 27 MHz-derived frequency, monotonic reads across wrap boundaries, and clean failure on non-SCx200 systems or region conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/scx200_hrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_cmt.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/sh_cmt.c

Purpose: implements Renesas/SuperH Compare Match Timer variants as clockevent and clocksource providers. It covers 16-bit, 32-bit, 48-bit, and R-Car Gen2/3/4 CMT layouts with shared or per-channel start/stop registers.

Important APIs, types, and functions: `struct sh_cmt_info` describes model width, channel mask, overflow bits, and accessors; `struct sh_cmt_channel` holds channel MMIO, match values, flags, locks, clockevent, clocksource, and cycle extension state; `struct sh_cmt_device` stores platform resources, clock rate, and channel array. Key routines include register accessors, `sh_cmt_get_counter()`, `sh_cmt_enable()/disable()`, `sh_cmt_clock_event_program_verify()`, `sh_cmt_interrupt()`, clocksource enable/read/suspend/resume, clockevent state/next callbacks, and `sh_cmt_setup()`.

Control flow: platform probe enables runtime PM, resolves model data from OF or platform data, prepares/enables `fck`, computes the effective timer rate, maps registers, allocates channels, and assigns channel 0 to clockevents and channel 1 to clocksource, or one channel to both if only one exists. Clockevent registration requests per-channel IRQs. Clocksource registration uses an enable callback, so hardware starts only when selected. Interrupts clear status, extend total cycles for single-channel source mode, run the clockevent handler unless skipped, and reprogram compare values under lock.

State and persistence: state is held in channel flags, `match_value`, `next_match_value`, `total_cycles`, `cs_enabled`, runtime PM/syscore markings, and hardware compare/counter/control registers. No disk persistence exists. Single-channel mode uses software cycle extension across compare wraps.

Dependencies and integration points: integrates with platform/OF matching, early platform timers on SuperH, PM runtime/genpd, common clock framework, IRQ core, clocksource, clockevents, and R-Car channel clock enable registers.

Risks: compare reprogramming is race-prone because hardware can wrap while software changes CMCOR; the `FLAG_REPROGRAM` and `FLAG_SKIPEVENT` logic is safety-critical. Register width, channel masks, real hardware indexes, and R-Car `CMCLKE` handling vary by model. Test signals include event and source registration on each model, one-channel and two-channel configurations, no missed one-shot deadlines under stress, suspend/resume with genpd, and correct behavior as earlytimer and normal platform driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_cmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_mtu2.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/sh_mtu2.c

Purpose: supports the SuperH/Renesas MTU2 block as a periodic clockevent provider. Unlike CMT and TMU, this driver does not register a clocksource.

Important APIs, types, and functions: `struct sh_mtu2_device` stores platform device, mapped base, `fck`, shared-register lock, channels, and clockevent availability. `struct sh_mtu2_channel` stores channel base and embedded clockevent. Important paths are `sh_mtu2_read()/write()`, `sh_mtu2_start_stop_ch()`, `sh_mtu2_enable()`, `sh_mtu2_disable()`, `sh_mtu2_interrupt()`, clockevent state callbacks, `sh_mtu2_setup_channel()`, and `sh_mtu2_probe()`.

Control flow: probe handles early-platform retention, enables runtime PM, allocates the device, prepares the functional clock, maps registers, counts IRQs, allocates channel structures, and for each channel tries to find a named IRQ like `tgi0a`. Channels without declared interrupts are skipped. Enabling a channel gets runtime PM, marks the device as syscore, enables the clock, stops the channel, computes a periodic period at clock/64, programs TGRA compare-match clear mode, enables TGRA interrupts, and starts the channel. The ISR acknowledges TGFA and dispatches the clockevent handler.

State and persistence: state is in the device/channel structs, prepared clock, runtime PM/syscore state, shared TSTR bits, and channel registers. There is no persistent storage and no clocksource state.

Dependencies and integration points: uses platform/OF matching, named platform IRQs, common clock framework, runtime PM/genpd, early platform timer hooks on SuperH, and clockevent registration.

Risks: only periodic mode is implemented; callers expecting one-shot behavior need another timer. Named IRQ resources must match `tgi%ua`. The shared start/stop register is protected by a raw spinlock and must remain synchronized across channels. Test signals include periodic tick delivery, correct clock/64 period, clean skip of channels without IRQs, runtime PM transitions, and earlytimer retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_mtu2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_tmu.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/sh_tmu.c

Purpose: implements the SuperH/Renesas Timer Unit as both a down-counting clocksource and a periodic/one-shot clockevent provider, usually using channel 0 for events and channel 1 for source.

Important APIs, types, and functions: `enum sh_tmu_model` distinguishes SH3 register layout from the normal layout. `struct sh_tmu_channel` contains channel base, IRQ, periodic value, clockevent, clocksource, enable count, and source-enabled flag. Key functions are `sh_tmu_read()/write()`, `sh_tmu_start_stop_ch()`, `sh_tmu_enable()/disable()`, `sh_tmu_set_next()`, `sh_tmu_interrupt()`, clocksource read/enable/suspend/resume, clockevent state/next callbacks, `sh_tmu_channel_setup()`, and `sh_tmu_setup()`.

Control flow: probe enables runtime PM, parses DT channel count or platform data, prepares/enables `fck`, computes `rate = clk / 4`, maps memory, allocates channels, registers channel 0 as clockevent and channel 1 as clocksource. Clockevent registration configures both periodic and oneshot callbacks and requests the channel IRQ. The source enables the channel lazily and reads inverted `TCNT`. For an event, `sh_tmu_set_next()` stops the channel, acknowledges status, enables interrupt, programs reload/count, and restarts.

State and persistence: state is per channel and in hardware TCOR/TCNT/TCR/TSTR registers. `enable_count` allows a channel to remain enabled when shared by source/event contexts or across suspend handling. No disk persistence exists.

Dependencies and integration points: integrates with platform/OF, early SuperH platform timers, PM runtime/genpd, common clock framework, clocksource, clockevents, and IRQ core.

Risks: register offsets differ for SH3 versus standard TMU. Enable-count correctness is critical to avoid disabling a clocksource still in use. The clocksource is a down-counter and must stay programmed with max timeout. Test signals include channel assignment, one-shot and periodic event behavior, clocksource monotonicity, PM suspend/resume with enable_count preserved, valid `#renesas,channels`, and earlytimer retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/sh_tmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-armada-370-xp.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-armada-370-xp.c

Purpose: supports Marvell Armada 370, Armada 375, and Armada XP timers. A global timer 0 is used as a down-counting clocksource/sched_clock/delay timer, while local per-CPU timer 0 instances provide periodic and one-shot clockevents.

Important APIs, types, and functions: global state includes `timer_base`, `local_base`, `timer_clk`, `timer25Mhz`, `enable_mask`, `ticks_per_jiffy`, and per-CPU `armada_370_xp_evt`. Important paths are `local_timer_ctrl_clrset()`, `armada_370_xp_clkevt_next_event()`, `armada_370_xp_clkevt_shutdown()`, `armada_370_xp_clkevt_set_periodic()`, `armada_370_xp_timer_interrupt()`, hotplug callbacks, syscore suspend/resume callbacks, and compatible-specific init functions.

Control flow: compatible init chooses a clock source: Armada XP requires the fixed clock, Armada 375 prefers fixed but can fall back to divided SoC clock, Armada 370 uses divided SoC clock. Common init maps global and local register spaces, programs 25 MHz or divider mode, starts global timer 0 free-running, registers delay timer, sched_clock, and MMIO clocksource, allocates per-CPU clockevents, requests the percpu IRQ from interrupt index 4, installs CPU hotplug callbacks, and registers syscore ops. CPU startup configures local timer mode, registers the clockevent, and enables the percpu IRQ.

State and persistence: global state is singleton and SoC-mode dependent. Syscore suspend caches global and local control registers and resume reloads max values and restores controls. Per-CPU event state lives in allocated clockevent devices and local timer registers.

Dependencies and integration points: uses OF clocks/address/IRQ parsing, percpu IRQs, CPU hotplug, clocksource MMIO helpers, sched_clock, delay timer registration, syscore ops, and atomic MMIO modify helpers.

Risks: Armada XP must use the stable fixed timer to avoid cpufreq-sensitive timekeeping. Interrupt index and local/global register resources are DT-sensitive. Test signals include cpufreq stability on XP, per-CPU ticks through hotplug, delay timer registration, suspend/resume restoration, and correct fallback behavior on Armada 375.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-armada-370-xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-pit.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-pit.c

Purpose: supports the AT91SAM926x Periodic Interval Timer as a combined periodic clockevent and software-extended clocksource running from master clock divided by 16.

Important APIs, types, and functions: `struct pit_data` holds the clockevent, clocksource, MMIO base, cycle length, accumulated count, IRQ, and master clock. Main paths are `read_pit_clk()`, `pit_clkevt_shutdown()`, `pit_clkevt_set_periodic()`, `at91sam926x_pit_reset()`, suspend/resume callbacks, `at91sam926x_pit_interrupt()`, and `at91sam926x_pit_dt_init()`.

Control flow: DT init allocates state, maps registers, gets/enables the master clock, parses IRQ, computes `pit_rate` and the HZ cycle value, resets and starts the PIT without IRQ, registers a clocksource whose mask combines PICNT and interval width, requests the shared timer IRQ, and registers a periodic-only clockevent. Periodic mode updates the software count using `PIVR`, then enables PIT interrupts. The ISR checks PIT status, folds elapsed hardware intervals into `cnt`, and invokes the event handler.

State and persistence: persistent runtime state is `data->cnt`, which extends the PIT's interval counter into a clocksource. Hardware mode register controls whether IRQs are enabled. Suspend disables the timer; resume resets it without enabling IRQ until periodic mode is selected again.

Dependencies and integration points: depends on OF address/IRQ/clock parsing, shared IRQ handling, clocksource, clockevents, and raw local IRQ save around clocksource reads.

Risks: this is periodic-only and uses software accumulation, so delayed interrupts and status reads must be correct or timekeeping drifts. `cycle - 1` must fit the PIT interval field. Test signals include stable periodic ticks, correct accumulated clocksource under delayed interrupts, suspend/resume reset, shared IRQ returning `IRQ_NONE` when appropriate, and no cycle-size warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-pit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-st.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-st.c

Purpose: supports the AT91RM9200 system timer using its 32 kHz counter as both clocksource and periodic/one-shot clockevent source.

Important APIs, types, and functions: global state includes `last_crtr`, `irqmask`, `clkevt`, `regmap_st`, and `timer_latch`. `read_CRTR()` stabilizes asynchronous counter reads. `at91rm9200_timer_interrupt()`, `clkdev32k_disable_and_flush_irq()`, `clkevt32k_shutdown()`, `clkevt32k_set_oneshot()`, `clkevt32k_set_periodic()`, `clkevt32k_next_event()`, and `atmel_st_timer_init()` are the key routines.

Control flow: init obtains the syscon regmap, disables and clears timer-related interrupts, requests the shared IRQ, enables the slow clock, computes the HZ latch, sets the realtime prescaler, registers the clockevent with a minimum delta of two ticks, and registers the 20-bit `32k_counter` clocksource. One-shot mode uses the alarm register; periodic mode uses PIT interrupts. The ISR masks status by `irqmask`, handles alarms directly, and for periodic mode loops while the counter has advanced by at least one latch to deliver delayed ticks.

State and persistence: `last_crtr` tracks the last periodic tick point and is reset when interrupts are flushed. `irqmask` records the active mode. There is no disk persistence; hardware registers hold interrupt enables, alarm, and period.

Dependencies and integration points: integrates with syscon/regmap, Atmel ST register definitions, slow clock, OF IRQ parsing, clocksource, and clockevents.

Risks: the counter is asynchronous and not strictly monotonic unless read twice until stable. One-shot alarm hardware uses absolute time and requires minimum delta two to avoid wrap-delayed matches. Test signals include 32 kHz clocksource registration, one-shot alarm events, periodic delayed-tick catchup, shared IRQ behavior, and stable reads under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-tcb.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-tcb.c

Purpose: uses an Atmel Timer Counter Block as a high-resolution clocksource, sched_clock, delay timer, and optional channel-2 clockevent. Older 16-bit hardware chains channels 0 and 1 into a 32-bit source; newer 32-bit hardware uses channel 0 alone.

Important APIs, types, and functions: global `tcaddr`, `tcb_cache`, and `bmr_cache` support timer access and suspend state. Clocksource functions are `tc_get_cycles()`, `tc_get_cycles32()`, `tc_clksrc_suspend()`, and `tc_clksrc_resume()`. Clockevent functions include `tc_shutdown()`, `tc_set_oneshot()`, `tc_set_periodic()`, `tc_next_event()`, `ch2_irq()`, and `setup_clkevents()`. Setup helpers are `tcb_setup_dual_chan()`, `tcb_setup_single_chan()`, and `tcb_clksrc_init()`.

Control flow: init runs once, maps the parent TCB, obtains channel and slow clocks, parses an IRQ, matches counter width, disables all interrupts, enables channel 0 clock, chooses the best divisor over roughly 5 MHz, configures either single-channel or chained dual-channel clocksource, registers the clocksource, sets up channel 2 clockevents, then registers sched_clock and delay timer. Channel 2 uses RC compare in periodic or oneshot mode.

State and persistence: suspend caches CMR/IMR/RC/clock-enable state for all three channels plus BMR, and resume restores channels and synchronizes them. `tcaddr` is the singleton guard. Runtime state also lives in TC registers and enabled clocks.

Dependencies and integration points: depends on Atmel TCB SoC definitions, OF parent-node clocks/IRQs, clocksource, clockevents, sched_clock, delay timer, and syscore-style clocksource suspend callbacks.

Risks: divisor selection, 16-bit chaining, and channel-2 clock choice differ by hardware. For 16-bit event mode, channel 2 may use slow clock while the clocksource uses divided master clock. Test signals include both 16-bit and 32-bit compatible coverage, stable chained reads, clockevent periodic and oneshot operation, suspend/resume register restoration, and delay timer calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-tcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-cadence-ttc.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-cadence-ttc.c

Purpose: supports the Cadence Triple Timer Counter, using timer 1 as clocksource/sched_clock and timer 2 as clockevent. It handles 16- or 32-bit timer width and clock-rate change notifications.

Important APIs, types, and functions: `struct ttc_timer`, `struct ttc_timer_clocksource`, and `struct ttc_timer_clockevent` wrap per-timer MMIO, clocks, notifiers, and core devices. Important functions include `ttc_set_interval()`, `ttc_clock_event_interrupt()`, `__ttc_clocksource_read()`, `ttc_set_next_event()`, `ttc_shutdown()`, `ttc_set_periodic()`, `ttc_rate_change_clocksource_cb()`, `ttc_setup_clocksource()`, `ttc_rate_change_clockevent_cb()`, `ttc_setup_clockevent()`, and `ttc_timer_probe()`.

Control flow: built-in platform probe runs once, maps the TTC block, parses interrupt 1 for timer 2, reads optional `timer-width`, selects clock inputs based on each timer's clock-source bit, initializes timer 1 as a prescaled free-running clocksource, then initializes timer 2 as a prescaled interval clockevent and requests its IRQ. Event programming disables the counter, writes interval, resets, and re-enables it. The clocksource notifier adjusts the prescaler around power-of-two clock-rate changes; the event notifier updates clockevents frequency after rate changes.

State and persistence: state is heap allocated per role and retained for the kernel lifetime. Clocksource notifier caches old/new clock-control register values for abort handling. Hardware state is in TTC clock-control, count-control, interval, ISR, and IER registers.

Dependencies and integration points: uses platform driver probing, OF clocks/IRQ, clock notifiers, clocksource, clockevents, sched_clock, and module OF matching.

Risks: the clocksource prescaler notifier only accepts near-exact power-of-two rate ratios and must update before or after the parent change depending on direction. Event registration uses a fixed max delta of `0xfffe`, which may be too low for 32-bit mode. Test signals include probe-once behavior, correct timer-width mask, clock-rate change acceptance/rejection, periodic and oneshot events, and stable clocksource after clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-cadence-ttc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-clint.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-clint.c

Purpose: supports RISC-V CLINT MMIO timers and software interrupts, mainly for M-mode/no-MMU systems. It registers the CLINT mtime counter as clocksource/sched_clock, per-hart mtimecmp registers as one-shot clockevents, and CLINT software interrupt registers as SMP IPIs.

Important APIs, types, and functions: global pointers include `clint_ipi_base`, `clint_timer_cmp`, and `clint_timer_val`; `clint_timer_freq` comes from `riscv_timebase`. Important routines are `clint_send_ipi()`, `clint_clear_ipi()`, `clint_ipi_interrupt()`, `clint_get_cycles64()`, `clint_clock_next_event()`, `clint_timer_starting_cpu()`, `clint_timer_dying_cpu()`, `clint_timer_interrupt()`, and `clint_timer_init_dt()`.

Control flow: DT init validates all interrupt specifiers are either timer or software interrupt, maps both IRQs through parent domains, maps CLINT registers, sets global bases, registers clocksource and sched_clock, requests the timer percpu IRQ, creates an IPI mux and chained software interrupt handler on SMP, then installs CPU hotplug callbacks. CPU startup registers the local clockevent and enables timer and IPI percpu IRQs. `set_next_event` enables timer interrupts in CSR_IE and writes current time plus delta to the hart's compare register.

State and persistence: runtime state is global MMIO pointers, percpu clockevent structs, IRQ mappings, and IPI mux state. On M-mode builds `clint_time_val` is exported for legacy access. No persistent storage exists.

Dependencies and integration points: integrates with RISC-V hart ID mapping, CSR interrupt bits, irqdomain/chained IRQ APIs, percpu IRQs, IPI mux, clocksource, clockevents, sched_clock, and OF timer declarations.

Risks: hart ID indexing must match CLINT register layout. The code assumes both timer and IPI IRQs are present. Timer ISR clears `IE_TIE`, so future events rely on `set_next_event` re-enabling it. Test signals include timer and soft IRQ validation, SMP IPIs through mux, CPU hotplug event setup, correct 32-bit lo/hi counter reads on non-64-bit builds, and clocksource registration at `riscv_timebase`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-clint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-cs5535.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-cs5535.c

Purpose: registers a CS5535/CS5536 MFGPT timer as a clockevent device using the 32.768 kHz input divided by 16. It is a clockevent-only driver, not a clocksource.

Important APIs, types, and functions: global `cs5535_event_clock` holds the allocated MFGPT timer. The operations are `disable_timer()`, `start_timer()`, `mfgpt_shutdown()`, `mfgpt_set_periodic()`, `mfgpt_next_event()`, `mfgpt_tick()`, and `cs5535_mfgpt_init()`. A module parameter `irq` can select the MFGPT IRQ.

Control flow: module init allocates any working-domain MFGPT timer, configures the CMP2 IRQ, requests a shared timer IRQ, writes the clock scale and CMP2 event mode into the setup register, and registers a periodic/one-shot clockevent at `MFGPT_HZ`. Starting an event writes CMP2, clears the counter, and enables count/CMP2. The IRQ checks whether the event came from this timer, disables and clears it, restarts it for periodic mode, and dispatches the event handler.

State and persistence: state is singleton and module-global. Hardware state lives in MFGPT setup, compare, and counter registers. There is no disk persistence; cleanup paths only exist for init failure.

Dependencies and integration points: integrates with the CS5535 MFGPT allocation/IRQ API, Linux module parameters, shared IRQ handling, and clockevents.

Risks: the handler must distinguish shared IRQs correctly. `disable_timer()` clears compare conditions unconditionally to avoid races, so changes must preserve CMP clear behavior. The selected divisor fixes min/max delta behavior. Test signals include module load on CS5535/CS5536, chosen IRQ logged, periodic and oneshot tick delivery, correct `IRQ_NONE` for unrelated shared interrupts, and clean failure if no MFGPT is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-cs5535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-davinci.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-davinci.c

Purpose: supports TI DaVinci timers as clocksource, sched_clock, and one-shot clockevent providers. Standard mode uses TIM12 for events and TIM34 for source; a compare-offset mode uses TIM12 for both to avoid touching TIM34 when it may be used by DSP firmware.

Important APIs, types, and functions: `struct davinci_clockevent` wraps the event device, base, and compare offset. Global `davinci_clocksource` holds the source device, base, and counter offset for sched_clock. Important functions include `davinci_timer_init()`, `davinci_clockevent_set_next_event_std()`, `davinci_clockevent_set_next_event_cmp()`, `davinci_timer_irq_timer()`, `davinci_clocksource_init_tim34()`, `davinci_clocksource_init_tim12()`, `davinci_timer_register()`, and `of_davinci_timer_register()`.

Control flow: OF init collects MMIO and IRQ resources plus the clock, then calls the exported registration routine. Registration enables the clock, requests the memory region, maps it, resets the timer block into dual 32-bit unchained mode, allocates and configures a clockevent, requests the event IRQ, initializes the clocksource mode based on `cmp_off`, registers the clockevent, registers the clocksource, and installs sched_clock. Standard next-event mode reprograms TIM12 period and starts oneshot; compare mode writes a compare value at current time plus cycles.

State and persistence: runtime state is global source state, allocated event state, MMIO resource ownership, enabled clock, and timer control registers. There is no remove path for successful early registration.

Dependencies and integration points: integrates with `clocksource/timer-davinci.h`, OF address/IRQ tables, common clock framework, clocksource, clockevents, sched_clock, and external board code through `davinci_timer_register()`.

Risks: standard mode preserves TIM34 periodic operation while changing TIM12; compare mode must not disturb DSP-owned TIM34. IRQ resource indexes must match `DAVINCI_TIMER_CLOCKEVENT_IRQ`. Test signals include both standard and compare-offset configurations, TIM34 free-running source, TIM12 one-shot events, memory-region exclusion, and clean error unwinds on clock/IRQ/map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-davinci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-digicolor.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-digicolor.c

Purpose: supports Conexant Digicolor timers using Timer B as the down-counting clocksource/sched_clock and Timer C as the periodic/one-shot clockevent. Timer A is intentionally avoided because watchdog support owns it.

Important APIs, types, and functions: `struct digicolor_timer` holds the clockevent, base, `ticks_per_jiffy`, and timer ID. Helper operations are `dc_timer_disable()`, `dc_timer_enable()`, and `dc_timer_set_count()`. Main routines are `digicolor_clkevt_shutdown()`, `digicolor_clkevt_set_oneshot()`, `digicolor_clkevt_set_periodic()`, `digicolor_clkevt_next_event()`, `digicolor_timer_interrupt()`, `digicolor_timer_sched_read()`, and `digicolor_timer_init()`.

Control flow: OF init maps shared timer/watchdog registers non-exclusively, parses the IRQ for Timer C, obtains/enables the timer clock, computes periodic ticks, configures Timer B with `UINT_MAX` and starts it, registers sched_clock and a down-counting MMIO clocksource, requests the Timer C IRQ, assigns cpumask and IRQ, and registers the clockevent. Next-event and periodic callbacks disable Timer C, program count, and enable the desired mode.

State and persistence: singleton state is in `dc_timer_dev`, clockevent core registration, and hardware control/count registers. Timer B remains enabled as free-running source. There is no disk persistence.

Dependencies and integration points: depends on OF clock/address/IRQ parsing, clocksource MMIO helpers, clockevents, sched_clock, and coordination with the watchdog sharing the same register block.

Risks: the register map is shared with watchdog, so exclusive mapping or Timer A use would conflict. Clockevent min delta is registered as zero, so very small deltas depend on hardware behavior. Test signals include watchdog coexistence, Timer B monotonic inverted reads, Timer C event delivery, valid IRQ index for Timer C, and no failed shared register mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-econet-en751221.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-econet-en751221.c

Purpose: supports EcoNet EN751221-style MIPS SoC high precision timers as a 32-bit MMIO clocksource/sched_clock and per-CPU one-shot clockevents. Each hardware block contains two timers, so the driver maps enough blocks for all possible CPUs.

Important APIs, types, and functions: `econet_timer` stores MMIO bases and frequency, and `econet_timer_pcpu` holds per-CPU clockevent devices. Register helpers are `reg_ctl()`, `reg_compare()`, `reg_count()`, `ctl_bit_enabled()`, and `ctl_bit_pending()`. Main paths are `cevt_interrupt()`, `cevt_set_next_event()`, `cevt_init_cpu()`, `sched_clock_read()`, `cevt_dev_init()`, `cevt_init()`, and `timer_init()`.

Control flow: DT init obtains the CPU timer clock, maps `DIV_ROUND_UP(num_possible_cpus(), 2)` register blocks, registers a clocksource on timer 0 count, initializes per-CPU events, and registers sched_clock. Event init maps the shared percpu IRQ, initializes all possible CPU timers with compare set to `U32_MAX`, fills per-CPU clockevent fields, and installs a CPU hotplug state. CPU startup enables the appropriate timer bit, enables the percpu IRQ, and registers the clockevent. The ISR verifies that the current CPU timer is pending, writes compare to current count to clear/neutralize, and calls the handler.

State and persistence: state is static and marked `__ro_after_init` for bases/frequency. Per-CPU devices are permanent. Hardware compare/count/control bits hold event state.

Dependencies and integration points: integrates with OF clocks/address/IRQ, percpu IRQs, CPU hotplug, clocksource MMIO helper, clockevents, and sched_clock.

Risks: the number of mapped blocks depends on possible CPUs and two timers per block. `cevt_set_next_event()` rejects too-close deadlines using signed arithmetic and the minimum delta. Test signals include correct block mapping on 1- and 2-block SoCs, per-CPU pending checks, CPU hotplug setup, stable timer 0 clocksource, and `-ETIME` handling for close deadlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-econet-en751221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ep93xx.c

Purpose: supports Cirrus EP93xx timers using Timer 4, a 40-bit free-running down-counter, as clocksource/sched_clock and Timer 3, a 32-bit interrupting timer, as one-shot clockevent.

Important APIs, types, and functions: `struct ep93xx_tcu` holds the MMIO base and global `ep93xx_tcu` exposes it to callbacks. Main functions are `ep93xx_clocksource_read()`, `ep93xx_read_sched_clock()`, `ep93xx_clkevt_set_next_event()`, `ep93xx_clkevt_shutdown()`, `ep93xx_timer_interrupt()`, and `ep93xx_timer_of_init()`.

Control flow: OF init allocates state, maps registers, parses one IRQ, enables Timer 4 high-byte latching, registers a 40-bit clocksource using a custom read callback, registers sched_clock, requests the Timer 3 IRQ, and registers the one-shot clockevent at the fixed Timer 1/2/3 rate. Next-event programming disables/clears Timer 3, writes the load value, and enables it with mode and clock-select bits. The ISR clears Timer 3 by writing its clear register and dispatches the event handler.

State and persistence: state is global and singleton. Timer rates are fixed constants, not DT clocks. Runtime state is in Timer 3/4 control/value registers and the registered devices.

Dependencies and integration points: uses OF address/IRQ, non-atomic low-high 64-bit MMIO helper, clocksource MMIO wrapper with a callback that ignores the passed base, sched_clock, and clockevents.

Risks: Timer 4 read depends on the hardware low-read latching high byte. Fixed frequencies must match silicon. The clockevent name is `"timer1"` despite using Timer 3, which is harmless but confusing. Test signals include 40-bit monotonic source reads, Timer 3 interrupt delivery, no IRQ parse failure, and sched_clock stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-fsl-ftm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-fsl-ftm.c

Purpose: supports Freescale FlexTimer Module hardware using separate FTM instances for a 16-bit clocksource/sched_clock and a periodic/one-shot clockevent. It supports big-endian register access via DT.

Important APIs, types, and functions: `struct ftm_clock_device` stores source/event bases, periodic cycles, prescaler, and endian mode. Important helpers are `ftm_readl()/ftm_writel()`, `ftm_counter_enable()/disable()`, `ftm_irq_acknowledge()/enable()/disable()`, `ftm_reset_counter()`, `ftm_set_next_event()`, `ftm_evt_interrupt()`, `ftm_clockevent_init()`, `ftm_clocksource_init()`, clock setup helpers, `ftm_calc_closest_round_cyc()`, and `ftm_timer_init()`.

Control flow: DT init allocates singleton `priv`, maps event and source register ranges, parses IRQ, reads `big-endian`, enables four named clocks for event/source counter and FTM modules, computes a prescaler so `periodic_cyc` fits in 16 bits, initializes the source, initializes the event, and returns. Source setup programs CNTIN/MOD, resets the counter, registers sched_clock and an up-count MMIO clocksource, then enables the counter. Event setup initializes CNTIN/MOD, resets, requests IRQ, registers the clockevent, and enables the counter. One-shot programming disables the counter, resets, writes `MOD = delta - 1`, starts counting, and enables TOF interrupt.

State and persistence: global `priv` and the hardware registers hold all state. The prescaler value is used by both source and event timers. There is no persistent storage or successful-remove path.

Dependencies and integration points: uses OF clock names, FTM register definitions in `linux/fsl/ftm.h`, clocksource MMIO helpers, sched_clock, clockevents, and IRQF_IRQPOLL.

Risks: prescaler calculation increments `ps` while testing, so off-by-one changes can corrupt event rate. Endianness must match hardware. `delta - 1` underflows if clockevents passes zero. Test signals include big- and little-endian boot, 16-bit clocksource registration, periodic rate accuracy, one-shot shutdown after IRQ, and correct named-clock availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-fsl-ftm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-fttmr010.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-fttmr010.c

Purpose: supports Faraday FTTMR010-compatible timers and Aspeed AST2400/2500/2600 variants. It uses one timer as clocksource/sched_clock/delay timer and another as periodic/one-shot clockevent, with variant-specific control-bit layouts and interrupt clearing.

Important APIs, types, and functions: `struct fttmr010` stores base, clock rate, tick values, control masks, interrupt masks, endian/counter direction choices, and embedded clockevent. Main functions are the up/down current-timer and sched_clock readers, `fttmr010_timer_set_next_event()`, `fttmr010_timer_shutdown()`, `ast2600_timer_shutdown()`, `fttmr010_timer_set_oneshot()`, `fttmr010_timer_set_periodic()`, `fttmr010_timer_interrupt()`, `ast2600_timer_interrupt()`, `fttmr010_common_init()`, and the compatible-specific init wrappers.

Control flow: compatible-specific `TIMER_OF_DECLARE()` selects standard Faraday/Gemini/Moxart, Aspeed, or AST2600 initialization. Common init maps MMIO, obtains clock and IRQ, configures the clocksource timer with max load/match values and direction, registers sched_clock/clocksource/delay timer, initializes the clockevent timer, requests IRQ, and registers clockevents. Event programming writes load/match registers and enables interrupt/counter bits. AST2600 uses separate clear registers and different shutdown semantics.

State and persistence: runtime state is global through `local_fttmr`, clockevent data, hardware count/load/match/control/interrupt registers, and delay timer registration. There is no disk persistence.

Dependencies and integration points: integrates with OF clocks/address/IRQ, `clocksource_mmio_init()` or custom readers depending on direction, sched_clock, clockevents, current timer delay, and Aspeed/Faraday-compatible register layouts.

Risks: register control-bit positions differ between generic and Aspeed hardware; AST2600 has a distinct clear register. Counter direction affects read inversion and delay timer behavior. Test signals include all compatible variants, interrupt acknowledgement paths, periodic and oneshot event delivery, monotonic source reads, and delay timer calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-fttmr010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-goldfish.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-goldfish.c

Purpose: supports the Goldfish emulator timer as a combined clocksource and one-shot clockevent. It is used by virtual/emulated platforms rather than physical SoC timer blocks.

Important APIs, types, and functions: `struct goldfish_timer` stores MMIO base, clockevent, and clocksource. Helpers convert from clockevent/clocksource to the container. Important routines are `goldfish_timer_read()`, `goldfish_timer_set_oneshot()`, `goldfish_timer_shutdown()`, `goldfish_timer_next_event()`, `goldfish_timer_irq()`, and `goldfish_timer_init()`.

Control flow: initialization receives IRQ and base from architecture/platform code, allocates state, fills the clocksource and clockevent devices, requests the IRQ, registers the source, and registers the one-shot event device. Clocksource reads combine the timer's high/low registers to return current virtual time. Next-event programming writes the target time or alarm registers based on current counter plus delta. The IRQ clears/acknowledges the device and calls the event handler.

State and persistence: state is heap allocated and tied to the emulator timer MMIO region. The timer device maintains current time and alarm state. No persistent storage exists.

Dependencies and integration points: integrates with the Goldfish platform timer device, MMIO accessors, IRQ core, clocksource, and clockevents. It is typically wired by architecture setup rather than a DT `TIMER_OF_DECLARE()` in this file.

Risks: emulator register ordering and 64-bit read consistency determine monotonicity. Alarm programming must handle very small deltas and shutdown must prevent stale interrupts. Test signals include boot in Goldfish-based emulator, monotonic virtual clocksource reads, one-shot alarm delivery, no stale IRQ after shutdown, and correct behavior under VM pause/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-goldfish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-gx6605s.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-gx6605s.c

Purpose: supports the C-SKY GX6605S timer as a 32-bit free-running clocksource/sched_clock and one-shot clockevent using the `timer_of` helper.

Important APIs, types, and functions: register definitions cover status, value, control, config, divider, and initial value; `CLKSRC_OFFSET` selects the source timer area. Main routines are `gx6605s_timer_interrupt()`, `gx6605s_timer_set_oneshot()`, `gx6605s_timer_set_next_event()`, `gx6605s_timer_shutdown()`, the static `struct timer_of to`, `gx6605s_sched_clock_read()`, `gx6605s_clkevt_init()`, `gx6605s_clksrc_init()`, and `gx6605s_timer_init()`.

Control flow: OF init initializes timer resources through `timer_of_init()`, then configures the clockevent side at the base register range and the clocksource side at base plus `CLKSRC_OFFSET`. Clockevent setup clears divider/config and registers the device. Clocksource setup clears divider/initial value, resets and starts the source timer, registers sched_clock, and registers an up-counting MMIO clocksource. A next-event call resets the event timer, writes `ULONG_MAX - delta` to `TIMER_INI` so overflow occurs after the requested delta, and starts the timer. The ISR clears status, writes zero to `TIMER_INI`, and invokes the event handler.

State and persistence: `timer_of` stores base, clock, IRQ, and embedded clockevent. Hardware state is in per-timer value/config/control registers. There is no persistent storage or multi-instance handling beyond the static `timer_of`.

Dependencies and integration points: depends on `timer-of.h`, OF compatible `"csky,gx6605s-timer"`, clocksource MMIO helper, sched_clock, and clockevents.

Risks: event and source timers are separated by a fixed offset, so register-map changes are risky. Shutdown must clear enable/IRQ bits to avoid stale oneshot interrupts. Test signals include source timer monotonicity, one-shot event delivery, status clear behavior, correct clock rate from `timer_of`, and clean init through DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-gx6605s.c -->
