# Research Report: subset-b-001190

Grouped research for clocksource timer drivers under `sources/distributed-fs/ceph-client/drivers/clocksource`. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-gxp.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-gxp.c

Purpose: HPE GXP boot-time timer driver providing a 32-bit MMIO timestamp clocksource/sched_clock and a one-shot clockevent backed by timer0. It also exposes the shared timer register block to a watchdog child device through a later platform-driver probe.

Important APIs/types/functions: `struct gxp_timer` stores counter/control MMIO and `clock_event_device`; `gxp_timer_init()` is registered by `TIMER_OF_DECLARE("hpe,gxp-timer")`; `gxp_time_set_next_event()` arms timer0; `gxp_timer_interrupt()` acknowledges terminal-count state and dispatches `event_handler`; `gxp_timer_probe()` creates a `gxp-wdt` platform device. It uses `clocksource_mmio_init()`, `sched_clock_register()`, `clockevents_config_and_register()`, `request_irq()`, `of_iomap()`, and CCF clock APIs.

Control flow: init allocates the singleton, enables the DT clock, maps registers, initializes `system_clock`, registers the clocksource/sched_clock at the hardware clock rate, configures clockevents at fixed `TIMER0_FREQ`, then requests a shared timer IRQ. On an event, it clears TC, writes the count, enables the timer, and the ISR verifies TC before acknowledging and invoking the clockevent core.

State/persistence: global `gxp_timer` and `system_clock` are boot-lifetime state. The clock reference is not retained for later disable, and the watchdog child receives the timer counter base as platform data.

Dependencies/integration: device tree compatible `hpe,gxp-timer`, one clock, one IRQ, Linux clocksource/clockevents/sched_clock, platform bus, and watchdog driver naming contract.

Risks: duplicate `irq_of_parse_and_map()` call, no cleanup after a successful clocksource if later IRQ request fails, fixed clockevent frequency may diverge from `clk_get_rate()`, singleton lifetime, and shared IRQ requires correct TC filtering. Test signals include DT boot logs, `/proc/timer_list`, clocksource selection, one-shot tick operation, and watchdog child creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-gxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-gpt.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-gpt.c

Purpose: Freescale/NXP i.MX GPT driver supporting several hardware generations as both clocksource/sched_clock and one-shot clockevent.

Important APIs/types/functions: `enum imx_gpt_type` separates MX1, MX21, MX31, and MX6DL programming models; `struct imx_timer` holds MMIO, clocks, IRQ, variant ops, and `clock_event_device`; `struct imx_gpt_data` carries register offsets and callbacks. `mxc_clocksource_init()`, `mxc_clockevent_init()`, `_mxc_timer_init()`, and `mxc_timer_init_dt()` form the init path. Variant functions implement IRQ enable/disable/ack, TCTL setup, and next-event programming.

Control flow: DT match selects a variant, maps one GPT instance, gets IRQ and `ipg` plus `osc_per`/`per` clocks, enables clocks, resets control/prescaler, starts the GPT in free-running mode, registers the counter as clocksource/sched_clock, then registers and requests the clockevent IRQ. `set_next_event()` writes compare as current count plus delta and returns `-ETIME` if the target already passed. The ISR reads status, acknowledges through the variant callback, and invokes the event handler.

State/persistence: one static `initialized` gate permits one instance only. `sched_clock_reg` and optional ARM `delay_timer` point at the chosen counter for boot lifetime. No runtime persistence beyond MMIO register state and clockevent mode.

Dependencies/integration: many `TIMER_OF_DECLARE()` compatible strings for i.MX generations, CCF clocks, DT IRQ, ARM delay timer when enabled, clocksource/clockevents core.

Risks: variant-compatible quirks, legacy i.MX6Q/DL compatibility workaround, incomplete cleanup on some failure paths, single-instance assumption, and compare race sensitivity near min delta. Test signals are successful boot with expected compatible, stable sched_clock, clockevent one-shot tick, and no `-ETIME` storms under high interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-gpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-sysctr.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-sysctr.c

Purpose: NXP i.MX system counter compare driver used as a one-shot clockevent against a 64-bit free-running system counter.

Important APIs/types/functions: `struct sysctr_private` stores CMPCR baseline and low/high counter offsets. `to_sysctr` is a static `timer_of` requesting base, clock, and IRQ. `sysctr_read_counter()` performs stable high/low/high reads. `sysctr_set_next_event()` programs `CMPCV_HI/LO`, `sysctr_timer_enable()` toggles compare enable, and `sysctr_timer_interrupt()` disables/acknowledges before dispatching.

Control flow: `__sysctr_timer_init()` allocates private data, calls `timer_of_init()`, optionally divides the clock rate by `SYS_CTR_CLK_DIV` unless `nxp,no-divider` is present, stores CMPCR with EN cleared, and sets CPU mask/private data. The standard and i.MX95 init wrappers choose different read offsets and register the clockevent. Events disable compare, read current 64-bit counter, add delta, write compare high/low, and re-enable.

State/persistence: static `to_sysctr` and heap private data persist for boot lifetime. CMPCR base bits are preserved so enable/disable does not clobber other compare control bits.

Dependencies/integration: `timer-of` helper, DT compatibles `nxp,sysctr-timer` and `nxp,imx95-sysctr-timer`, named clock `per`, one IRQ, clockevents core.

Risks: no clocksource registration here, so another system counter source must exist; singleton `to_sysctr`; allocation is not freed on later success; low/high offset selection must match SoC; compare high is masked to 20 bits. Tests should verify correct DT property clock divider, one-shot delivery, no stale ISTAT after shutdown, and i.MX95 offset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-sysctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-tpm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-tpm.c

Purpose: i.MX7ULP TPM timer driver providing a free-running up-counting clocksource/sched_clock/delay timer and a channel-0 software-compare one-shot clockevent.

Important APIs/types/functions: global `counter_width` and `timer_base`; `to_tpm` static `timer_of`; helpers disable/enable the compare channel, acknowledge CH0F, and read `TPM_CNT`. `tpm_set_next_event()` writes `TPM_C0V` and checks for missed deadlines. `tpm_clockevent_init()` and `tpm_clocksource_init()` register framework devices.

Control flow: init enables the `ipg` clock first for register access, then `timer_of_init()` acquires base/clock/IRQ. It discovers counter width from `TPM_PARAM`, resets TPM state, clears W1C flags, sets prescaler to div8 for 32-bit or div128 for 16-bit, sets `MOD` to max for free-running mode, registers clockevent, then clocksource. IRQ acknowledges channel flag and invokes the event handler.

State/persistence: static base and counter width become read-mostly boot state. The TPM counter keeps running after initialization; clockevent state is controlled by channel mode/interrupt enable.

Dependencies/integration: compatible `fsl,imx7ulp-tpm`, named `ipg` and `per` clocks, `timer-of`, ARM delay timer and sched_clock when `CONFIG_ARM`, MMIO clocksource.

Risks: `timer_of_init()` failure after enabling `ipg` leaks that clock; busy-wait for C0V synchronization can spin if hardware misbehaves; 16-bit mode has lower rating/range; rate is shifted by prescaler and must match register setup. Test signals include 16-bit/32-bit DT coverage, no missed min-delta events under bus contention, and clocksource monotonicity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-imx-tpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-integrator-ap.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-integrator-ap.c

Purpose: ARM Integrator/AP timer driver using one SP-style timer as 16-bit clocksource/sched_clock and another as periodic/one-shot clockevent, chosen by DT aliases.

Important APIs/types/functions: uses `timer-sp.h` register definitions. `integrator_clocksource_init()` configures a down-counting periodic source with optional div16. `integrator_clockevent_init()` computes divisor/reload, requests IRQ, and registers `integrator_clockevent`. Clockevent callbacks manipulate `TIMER_LOAD` and `TIMER_CTRL`.

Control flow: OF init maps the timer node, enables its clock, disables the timer, then reads `arm,timer-primary` or `arm,timer-secondary` from `/aliases`. Primary initializes clocksource; secondary parses IRQ and initializes clockevent; other nodes are disabled/ignored. The ISR clears `TIMER_INTCLR` and dispatches the event handler.

State/persistence: `sched_clk_base`, `clkevt_base`, and `timer_reload` are global. Timer role is persisted only by hardware registers and alias selection; no dynamic removal path.

Dependencies/integration: DT compatible `arm,integrator-timer`, `/aliases` properties, one clock per node, IRQ on secondary, clocksource/clockevents/sched_clock.

Risks: alias path handling is critical; comments note primary lacks IRQ. Error paths do not consistently unmap/disable clocks. 16-bit counter has limited range and uses divisors to fit rates. Tests should boot with primary/secondary aliases, check exactly one clocksource and one clockevent, verify periodic tick and one-shot mode, and inspect warnings for unused timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-integrator-ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ixp4xx.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ixp4xx.c

Purpose: Intel IXP4xx OS timer driver for timestamp clocksource/sched_clock/delay timer, timer1 clockevent, and watchdog child platform-device creation.

Important APIs/types/functions: `struct ixp4xx_timer` stores base, latch, clockevent, and optional ARM delay timer. `ixp4xx_timer_register()` initializes hardware and framework devices. Clockevent callbacks program `OSRT1`; `ixp4xx_clocksource_read()` uses `OSTS`; `ixp4xx_timer_probe()` registers `ixp4xx-watchdog`.

Control flow: OF init maps MMIO, parses IRQ, then calls register with a hard-coded 66.666 MHz frequency. Registration resets timer1 and timestamp counter, registers custom clocksource, requests timer1 IRQ, registers clockevent, sched_clock, and delay timer. Periodic mode writes a latch rounded to the hardware’s ignored low bits; oneshot writes enable/one-shot bits and later reload value.

State/persistence: singleton `local_ixp4xx_timer` backs fast reads and watchdog platform data. Hardware timer registers are shared with watchdog code.

Dependencies/integration: compatible `intel,ixp4xx-timer`, platform driver for child device, ARM delay timer, clocksource/clockevents, fixed platform timer frequency.

Risks: hard-coded clock frequency until DT fixed clocks exist; no watchdog probe guard if timer init failed other than singleton use; clocksource registration errors are not checked; raw MMIO access and shared watchdog registers require careful ownership. Test signals include timer tick, clocksource stability, watchdog registration, and correct latch behavior at HZ boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ixp4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-keystone.c

Purpose: TI Keystone broadcast clockevent driver for a 64-bit timer block. It does not register a clocksource.

Important APIs/types/functions: static `timer` holds MMIO base, HZ period, and `clock_event_device`. `keystone_timer_config()` disables the timer, resets counters, writes 64-bit period registers, and re-enables in one-shot or periodic mode with explicit I/O barriers. `keystone_set_next_event()`, `keystone_shutdown()`, and `keystone_set_periodic()` implement clockevent callbacks.

Control flow: `keystone_timer_init()` parses IRQ and base, enables the input clock, disables and resets the hardware, unresets the 64-bit timer, initializes counters, enables timer interrupt generation, requests IRQ, fills the clockevent structure, and registers it. IRQ dispatch is simple because hardware interrupt enable/status was configured globally.

State/persistence: a single static `timer` persists for boot lifetime. `hz_period` is derived from the enabled clock rate. Hardware mode/counter registers store runtime state.

Dependencies/integration: compatible `ti,keystone-timer`, one clock, one IRQ, clockevents core. Uses `__iowmb()` because relaxed MMIO calls are intentionally paired with explicit ordering.

Risks: global singleton, no cleanup for clocksource because none exists, limited error unwinding after `request_irq()` failure, and correctness depends on barriers around disable/write/enable sequence. Test signals include periodic and one-shot clockevent modes, IRQ delivery, clock rate log, and suspend/idle interactions when used as a broadcast event source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-loongson1-pwm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-loongson1-pwm.c

Purpose: Loongson-1 PWM timer driver exposing one PWM timer as both clockevent and an emulated 24-bit clocksource.

Important APIs/types/functions: `ls1x_to` is a `timer_of` with base/clock/IRQ. `struct ls1x_clocksource` wraps a `clocksource` plus MMIO base and ticks-per-jiffy. Clockevent helpers set HRC/LRC period, clear/start/stop counter, acknowledge IRQ, and callbacks implement periodic, shutdown, resume, and next-event.

Control flow: init calls `timer_of_init()`, registers the clockevent with min 1 and 24-bit max, points the clocksource at the same base, stores period, and registers `ls1x_clocksource`. The ISR acknowledges, clears, restarts the PWM timer, then dispatches. Clocksource read combines `jiffies * ticks_per_jiffy` with the current PWM counter and uses a raw spinlock plus static old values to avoid apparent backward movement before jiffies catches up.

State/persistence: shared raw spinlock protects clockevent programming and clocksource read side effects. Static `old_count`/`old_jifs` inside the read function persist across calls.

Dependencies/integration: compatible `loongson,ls1b-pwmtimer`, `timer-of`, jiffies, clocksource/clockevents, IRQ.

Risks: clocksource read has side effects, making retry semantics delicate; the 24-bit mask may not represent the larger jiffies-composed value; sharing the same PWM hardware for event and source is sensitive to restarts. Tests should stress monotonic time, missed IRQ handling, periodic and one-shot mode, and lockdep/interrupt latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-loongson1-pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-lpc32xx.c

Purpose: NXP LPC32xx/18xx/43xx timer driver that uses separate DT timer nodes/instances for one free-running clocksource and one match-based clockevent.

Important APIs/types/functions: `struct lpc32xx_clock_event_ddata` holds clockevent base and ticks-per-jiffy. `lpc32xx_clocksource_init()` configures a free-running timer and registers clocksource, sched_clock, and delay timer. `lpc32xx_clockevent_init()` configures match channel 0, registers clockevent, and requests IRQ.

Control flow: `lpc32xx_timer_init()` tracks static `has_clocksource` and `has_clockevent`; first compatible node successfully becomes clocksource, second becomes clockevent. Clockevent next-event resets the counter, writes MR0, and enables the timer; periodic mode enables interrupt/reset-on-match; one-shot adds stop-on-match. ISR clears MR0 interrupt and invokes handler.

State/persistence: global `clocksource_timer_counter` supports sched_clock and delay reads. Static flags control role assignment across compatible nodes. Clockevent state lives in the global ddata object.

Dependencies/integration: compatible `nxp,lpc3220-timer`, named `timerclk`, DT IRQ for event timer, clocksource/clockevents/sched_clock/current-timer-delay.

Risks: role assignment depends on DT probe order and successful init; no direct source/event distinction in compatible; cleanup on partial failures is present but boot-lifetime resources are retained. Test signals include two timer nodes, one selected clocksource, one clockevent IRQ, MR0 interrupt clearing, and delay timer registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek-cpux.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek-cpux.c

Purpose: MediaTek CPUX General Purpose Timer wrapper setup for SoCs where CPUXGPT feeds the AArch64 system timer. It registers a low-rated clockevent control shim without declaring a timer IRQ.

Important APIs/types/functions: `mtk_cpux_readl()` and `mtk_cpux_writel()` access indexed CPUX registers through wrapper index/data registers. `mtk_cpux_set_irq()` masks/unmasks per-CPU timer IRQ bits for possible CPUs. `mtk_cpux_init()` configures divider and global enable. The static `timer_of to` requests only base and clock.

Control flow: init obtains base/clock via `timer_of_init()`, warns if the supplied clock exceeds the supported range, writes DIV2 to produce a 13 MHz timer from 26 MHz input, enables all CPUXGPT timers, then registers the clockevent with sync-tick minimum. Shutdown masks CPUX IRQ bits but intentionally leaves the timer running because firmware may depend on it; resume unmasks.

State/persistence: global `to` keeps MMIO/clock state. CPUX global control remains enabled for boot lifetime. IRQ mask state is the only clockevent state changed by callbacks.

Dependencies/integration: compatible `mediatek,mt6795-systimer`, `timer-of`, CPU possible mask, AArch64 architectural timer/firmware expectations.

Risks: no actual `set_next_event()` or IRQ handler, so it relies on the architecture timer path; disabling the timer is explicitly unsafe; unsupported clock frequencies may still boot with timing instability; indexed register access must be serialized by hardware/boot context. Test signals include boot without lockups, correct 13 MHz configuration, low clockevent rating, and suspend/resume IRQ masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek-cpux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek.c

Purpose: MediaTek timer driver supporting two hardware models: older GPT blocks with clocksource plus clockevent, and newer system timer blocks providing one-shot clockevents only.

Important APIs/types/functions: one static `timer_of to` is configured differently by `mtk_gpt_init()` and `mtk_syst_init()`. GPT helpers stop/setup/start timers, configure free-running source timer 2, enable/ack IRQs, and manage suspend/resume. SYST helpers program countdown value and control register bits.

Control flow: GPT init sets clockevent callbacks and IRQ handler, calls `timer_of_init()`, configures timer 2 as free-running clocksource/sched_clock, configures timer 1 for events, registers clockevent, and enables its IRQ. SYST init assigns one-shot callbacks/handler, initializes resources, and registers clockevent. Event programming always disables/stops before writing compare/countdown and re-enables interrupt. Interrupt handlers acknowledge then invoke the event handler.

State/persistence: global `to` and `gpt_sched_reg` persist. GPT suspend disables and acknowledges all interrupts to avoid firmware suspend blockage; resume reenables the event IRQ.

Dependencies/integration: compatibles `mediatek,mt6577-timer` and `mediatek,mt6765-timer`, `timer-of`, clocksource/clockevents/sched_clock, DT IRQ and clock.

Risks: single static `to` prevents simultaneous GPT/SYST instances; GPT and SYST share names/global state; `mtk_gpt_suspend()` acknowledges all six timer IRQ bits; SYST lacks clocksource. Tests should cover both compatibles, IRQ ack behavior, suspend/resume, and clocksource selection on GPT platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-meson6.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-meson6.c

Purpose: Amlogic Meson6 timer driver using Timer E as 1 MHz clocksource/sched_clock/delay timer and Timer A as periodic/one-shot clockevent.

Important APIs/types/functions: global `timer_base`; `meson6_clkevt_time_stop/setup/start()` control Timer A; `meson6_timer_sched_read()` reads Timer E; `meson6_clockevent` describes clockevent callbacks; `meson6_timer_init()` wires DT resources and framework registration.

Control flow: init maps registers, parses IRQ, configures Timer E input clock to 1 us, registers sched_clock and MMIO clocksource, configures Timer A input clock to 1 us, stops Timer A, requests IRQ, fills cpumask/IRQ, and registers clockevent. Periodic mode loads `USEC_PER_SEC / HZ - 1`; one-shot mode starts nonperiodic and next-event reloads Timer A.

State/persistence: one global MMIO base for both timers. Timer E remains enabled as source; Timer A mode is controlled by event callbacks.

Dependencies/integration: compatible `amlogic,meson6-timer`, DT IRQ/base, clocksource/clockevents/sched_clock, optional ARM delay timer.

Risks: fixed 1 MHz programming assumes mux definitions and hardware behavior; init error paths do not consistently unmap; ISR does not explicitly acknowledge beyond hardware mode behavior; global singleton. Test signals include Timer E monotonicity, one-shot/periodic tick, ARM delay calibration, and correct mux register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-meson6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-microchip-pit64b.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-microchip-pit64b.c

Purpose: Microchip SAM9X60 PIT64B driver using two DT instances: first for clockevent, second for 64-bit clocksource/sched_clock/delay timer.

Important APIs/types/functions: `struct mchp_pit64b_timer` captures base, pclk, gclk, and precomputed mode; wrapper structs embed clockevent or clocksource. `mchp_pit64b_init_mode()` chooses GCLK or PCLK and prescaler for a target 5 MHz. `mchp_pit64b_reset()` resets/programs period/mode/IRQ and starts. Clocksource and clockevent init allocate persistent wrappers.

Control flow: `mchp_pit64b_dt_init()` uses static `inits`; case 0 initializes event timer with IRQ, case 1 initializes clocksource without IRQ. Per timer init obtains clocks and MMIO, computes mode/rate, then registers either event or source. Clockevent callbacks resume clocks if needed and reset PIT in periodic/one-shot mode; shutdown suspends clocks unless detached. ISR reads status to clear then calls event handler.

State/persistence: global `mchp_pit64b_cs_base`, `mchp_pit64b_ce_cycles`, delay timer, static init count, and allocated wrappers persist. Suspend/resume callbacks gate pclk/gclk.

Dependencies/integration: compatible `microchip,sam9x60-pit64b`, named `pclk`/`gclk`, CCF rate setting, clocksource/clockevents/sched_clock/delay.

Risks: DT instance order determines role; clocksource read uses a global base rather than per-instance pointer; clock rate selection has hardware pclk/gclk constraints; partial errors dispose IRQ/unmap but may leak clocks. Tests should cover two-node DT order, clock-rate logs, suspend/resume, 64-bit read atomicity, and event IRQ clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-microchip-pit64b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-milbeaut.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-milbeaut.c

Purpose: Socionext Milbeaut timer driver using channel 1 as down-counting clocksource/sched_clock and channel 0 as clockevent.

Important APIs/types/functions: static `timer_of to`; `mlb_config_clock_source()` configures source channel reload and count; `mlb_evt_timer_*()` helpers program event channel; `mlb_timer_interrupt()` clears underflow and dispatches. Clockevent callbacks implement periodic, one-shot, shutdown, and next-event.

Control flow: init acquires base/clock/IRQ via `timer_of_init()`, halves the source rate due to `MLB_TMR_DIV_CNT`, starts source channel in reload/count mode, registers down-counting clocksource and sched_clock, initializes event channel, then registers clockevent. Periodic writes `of_clk.period`, one-shot/next-event stop and restart without reload bit.

State/persistence: global `to` stores all resources. Timer channel registers persist clocksource and event state. Sched_clock reads inverted source timer value.

Dependencies/integration: compatible `socionext,milbeaut-timer`, `timer-of`, clocksource/clockevents/sched_clock, DT clock/IRQ.

Risks: clockevent registration uses `timer_of_rate()` rather than the divided source rate, so event and source rates intentionally differ; W1C/underflow clearing depends on writing modified TMCSR; singleton only. Test signals include underflow IRQ clearing, source rate correctness, periodic and one-shot behavior, and clocksource monotonicity for the down counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-milbeaut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mp-csky.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mp-csky.c

Purpose: C-SKY SMP private timer driver using CPU control registers for per-CPU clockevents and a CPU-register clocksource/sched_clock.

Important APIs/types/functions: per-CPU `struct timer_of csky_to` requests only the clock. `mtcr()` and `mfcr()` access private timer control, load, current value, and status registers. `csky_mptimer_starting_cpu()` registers each CPU clockevent; `csky_timer_interrupt()` clears status and dispatches; `csky_clocksource` reads `PTIM_CCVR`.

Control flow: init maps one common private IRQ from DT, requests it as percpu, calls `timer_of_init()` for each possible CPU to acquire clock metadata, registers clocksource/sched_clock at the timer rate, then installs CPU hotplug callbacks. CPU startup sets cpumask, enables percpu IRQ, and registers oneshot clockevent; CPU dying disables IRQ.

State/persistence: `csky_mptimer_irq` is global, and `csky_to` is per-CPU static state. No MMIO base is used; control register state is CPU-local.

Dependencies/integration: compatible `csky,mptimer`, DT IRQ and clock, arch `asm/reg_ops.h`, CPU hotplug, percpu IRQ infrastructure, `timer-of`.

Risks: rollback cleans timer_of resources but not percpu IRQ on all failures; clocksource rate uses last initialized CPU’s timer metadata; hardware must provide synchronized per-core counters. Test signals include CPU hotplug on/off, percpu IRQ affinity, one-shot event delivery, and stable cross-CPU time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-mp-csky.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-msc313e.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-msc313e.c

Purpose: MStar/SigmaStar MSC313E timer driver using first compatible timer as clocksource/sched_clock/delay and later timers as clockevents.

Important APIs/types/functions: `msc313e_timer_stop/start/setup/current_value()` handle 16-bit split registers. `msc313e_clksrc_init()` registers clocksource; `msc313e_clkevt_init()` allocates a `timer_of` and registers a clockevent. Static `msc313e_clkevt` is copied into each `timer_of`.

Control flow: `msc313e_timer_init()` increments `num_called`; first call initializes source, subsequent calls initialize event. For `sstar,ssd20xd-timer`, event init divides clock by `MSC313E_CLK_DIVIDER` and writes divider. Clockevent next/periodic paths stop, write high/low max, and start in one-shot or periodic. ISR directly dispatches the event handler.

State/persistence: global `msc313e_clksrc` and optional ARM delay state persist. The source path uses a stack `timer_of`; its base remains valid after init. Event path allocates persistent `timer_of` objects.

Dependencies/integration: compatibles `mstar,msc313e-timer` and `sstar,ssd20xd-timer`, `timer-of`, split 16-bit MMIO, optional ARM delay, clocksource/clockevents.

Risks: DT order controls source versus event role; clocksource uses `clocksource_mmio_init()` with custom read and base argument not used by read; event init leak on `timer_of_init()` failure; local IRQ disable is used for split register access. Tests should cover first/subsequent node ordering, SSD20x divider, split-register consistency, and event interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-msc313e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-npcm7xx.c

Purpose: Nuvoton NPCM/WPCM timer driver using timer0 as clockevent and timer1 as 24-bit down-counting clocksource.

Important APIs/types/functions: static `npcm7xx_to` is a `timer_of` with base/clock/IRQ. Clockevent callbacks manipulate TCSR0/TICR0. `npcm7xx_clocksource_init()` programs timer1 max count and registers MMIO down clocksource. `npcm7xx_clockevents_init()` initializes timer0 and registers clockevent.

Control flow: init calls `timer_of_init()`, divides input clock by prescale+1, optionally enables a second clock for timer1, initializes source then event, and logs base/IRQ. Periodic mode writes `timer_of_period()` to TICR0 and starts period/int/count bits; next-event writes requested value and starts. ISR clears T0 interrupt in TISR and dispatches.

State/persistence: one static `timer_of` keeps base/clock/IRQ. Timer1 clock source runs continuously; timer0 state follows clockevent mode. Optional second clock is enabled and retained.

Dependencies/integration: compatibles `nuvoton,wpcm450-timer` and `nuvoton,npcm750-timer`, `timer-of`, optional second clock, clocksource/clockevents.

Risks: second clock acquisition treats any non-NULL pointer as present before `IS_ERR()`; clocksource init return is ignored; clockevent cpumask fixed to CPU0; 24-bit source has limited range. Test signals include timer0 interrupts, timer1 down-count monotonic conversion, prescaler rate correctness, and boot log with base/IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-pit.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-pit.c

Purpose: NXP/Freescale Periodic Interrupt Timer driver supporting DT early init for VF610 and platform-driver probing for S32G2, with channel 2 as clocksource and channel 3 as per-CPU clockevent.

Important APIs/types/functions: `struct pit_timer` embeds clockevent and clocksource; per-CPU `pit_timers` maps CPU slots. Helpers enable/disable module/timer, set counters, and ack IRQ. `pit_timer_init()` handles one hardware instance; `pit_clockevent_starting_cpu()` registers CPU-local events via hotplug.

Control flow: init maps base, IRQ, clock, disables module, registers channel-2 source/sched_clock, initializes channel-3 event and IRQ for `pit_instances`, enables module, increments instance count, and when all expected instances are present installs a CPU hotplug state. Event programming disables channel, writes `delta - 1`, and enables interrupt. ISR acks, disables in oneshot because hardware auto-reloads, then dispatches.

State/persistence: global instance counters and `max_pit_instances` govern multi-instance setup. `sched_clock_base` points to the last clocksource channel. Per-CPU pointers persist allocated PIT objects.

Dependencies/integration: compatibles `fsl,vf610-pit` and `nxp,s32g2-pit`, platform driver match data, CCF clocks, CPU hotplug, IRQ affinity.

Risks: each PIT instance registers a clocksource, potentially multiple sources; error unwind after hotplug setup is incomplete; `sched_clock_base` may be overwritten by later instances; oneshot is software-emulated over repeating hardware. Tests should cover S32G2 two-instance CPU affinity, VF610 single instance, channel selection, and no repeated oneshot interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-pit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-stm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-stm.c

Purpose: NXP System Timer Module platform driver for S32G2, registering one STM instance per possible CPU as both a clocksource and a CPU-affine clockevent.

Important APIs/types/functions: `struct stm_timer` embeds base, rate, delta, saved counter, clockevent, clocksource, and module refcount. Clocksource callbacks use module get/put and suspend/resume counter save. Clockevent callbacks program channel 0 compare and update compare in ISR. `nxp_stm_timer_probe()` is a devm platform-driver probe guarded by `stm_instances_lock`.

Control flow: probe serializes instance assignment, ignores extra nodes beyond possible CPUs, maps MMIO, gets IRQ and enabled clock, allocates state, requests IRQ, registers clocksource/sched_clock, initializes per-CPU clockevent for current instance number, increments instances, and installs CPU hotplug when all possible CPUs have an instance. CPU startup forces IRQ affinity and registers clockevent with a 2 us minimum delta.

State/persistence: global `stm_instances`, per-CPU `stm_timers`, `stm_sched_clock`, and per-instance atomic module refcounts. Suspend stores counter and resumes restores it.

Dependencies/integration: platform compatible `nxp,s32g2-stm`, devm resources, CPU hotplug, IRQ affinity, CCF clock, module metadata.

Risks: each instance registers a clocksource and overwrites sched_clock pointer; hotplug only installs after all CPUs’ instances probed; periodic mode uses `rate` as delta, which is one second rather than `rate/HZ`; compare race returns `-ETIME`. Test signals include multi-node async probing, CPU hotplug, IRQ affinity, suspend/resume counter restore, and clockevent periodic correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-nxp-stm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.c

Purpose: shared helper for early device-tree timer drivers to acquire MMIO base, clock, and IRQ resources into a `struct timer_of`.

Important APIs/types/functions: `timer_of_init()` is the main exported init helper; `timer_of_cleanup()` releases resources. Internal helpers initialize and exit IRQ (`timer_of_irq_init/exit`), clock (`timer_of_clk_init/exit`), and base (`timer_of_base_init/exit`) resources.

Control flow: `timer_of_init()` checks flags in order: map base, enable/get clock and rate/period, request IRQ, then assigns a default clockevent name and stores the DT node. On failure it unwinds only resources acquired so far. IRQ acquisition prefers named IRQ then index; clock acquisition prefers named clock then index; base mapping uses `of_io_request_and_map()` when a name is supplied, otherwise `of_iomap()`.

State/persistence: it writes resource pointers, rate, period, IRQ number, and `np` into caller-owned `timer_of`. No global state. Resources are intended to persist for boot-lifetime timer users unless `timer_of_cleanup()` is called on init failure.

Dependencies/integration: DT OF address/IRQ/clock APIs, CCF, `request_irq()`, `clock_event_device`, and `timer-of.h` struct layout.

Risks: `timer_of_irq_exit()` frees IRQ using `to->clkevt`; callers must not mutate clkevt unexpectedly before cleanup. `timer_of_base_exit()` calls `iounmap()` even for regions mapped with request-and-map, so ownership expectations matter. It is `__init`, so runtime users should not call it. Tests are indirect: drivers using base/clock/IRQ combinations should fail cleanly on missing resources and not leak on early init errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.h -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.h

Purpose: private header defining the `timer_of` resource bundle used by many clocksource drivers to consolidate DT base, clock, IRQ, and clockevent state.

Important APIs/types/functions: flags `TIMER_OF_BASE`, `TIMER_OF_CLOCK`, and `TIMER_OF_IRQ` select resources. `struct of_timer_irq`, `of_timer_base`, and `of_timer_clk` describe requested resources and resulting handles. `struct timer_of` embeds a `clock_event_device`, device node, resource structs, and `private_data`. Inline accessors include `to_timer_of()`, `timer_of_base()`, `timer_of_irq()`, `timer_of_rate()`, and `timer_of_period()`.

Control flow: no executable control flow beyond inline conversion/access. Drivers fill fields before calling `timer_of_init()` from `timer-of.c`, then use accessors from callbacks and IRQ handlers.

State/persistence: this header defines caller-owned state layout; persistence depends on each driver’s allocation/static storage. `private_data` is an untyped extension point used by several drivers for SoC-specific offsets or width.

Dependencies/integration: `linux/clockchips.h` and the `timer_of_init()/timer_of_cleanup()` implementations. The embedded `clock_event_device` makes `container_of()` conversions central to IRQ and callback paths.

Risks: because `timer_of` embeds mutable `clock_event_device`, copying a preinitialized `clock_event_device` after IRQ request can change cleanup behavior. Accessors do not validate flags or NULL handles. Test signal is compile-time integration across all users and runtime init failure handling through cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-orion.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-orion.c

Purpose: Marvell Orion timer driver using timer0 as free-running down-counting clocksource/sched_clock/delay and timer1 as clockevent.

Important APIs/types/functions: global `timer_base` and `ticks_per_jiffy`; `orion_clkevt_next_event()`, shutdown, and periodic callbacks manipulate timer1 registers with `atomic_io_modify()`. `orion_timer_init()` performs DT resource setup and framework registration.

Control flow: init maps shared timer/watchdog registers, enables clock, parses timer1 IRQ at index 1, starts timer0 with reload/value `~0`, registers down-counting clocksource and sched_clock, requests timer1 IRQ, computes ticks-per-jiffy, registers clockevent, and registers delay timer. The clockevent ISR directly calls `orion_clkevt.event_handler()`; hardware status clearing is presumably handled by timer mode/control.

State/persistence: global base and clockevent object are boot lifetime. Timer registers are shared with watchdog hardware. Delay timer and sched_clock point at timer0.

Dependencies/integration: compatible `marvell,orion-timer`, clock, IRQ index 1, `atomic_io_modify()`, clocksource/clockevents/delay.

Risks: shared watchdog register block, no explicit interrupt status ack in ISR, cleanup gaps on resource failure, and CPU0-only cpumask. Test signals include IRQ index correctness, timer0 monotonic down-read, one-shot/periodic timer1 delivery, delay timer operation, and watchdog coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-owl.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-owl.c

Purpose: Actions Semi Owl timer driver using one internal timer slice as clocksource/sched_clock and another as one-shot clockevent.

Important APIs/types/functions: global base pointers select overall, source, and event timer blocks. `owl_timer_reset()` clears CTL/VAL/CMP; `owl_timer_set_enabled()` toggles enable while clearing PD semantics. `owl_timer_set_next_event()` programs compare and interrupt. `owl_timer_init()` maps resources and registers frameworks.

Control flow: init maps base, derives source base at `+0x08` and event base at `+0x14`, gets named IRQ `timer1`, gets the clock rate, resets/enables source, registers sched_clock and MMIO clocksource, resets event, requests IRQ, sets cpumask/IRQ, and registers one-shot dynamic IRQ clockevent. ISR writes PD to acknowledge pending event then dispatches.

State/persistence: global MMIO pointers persist. Source timer runs continuously; event timer is reset or enabled per callback.

Dependencies/integration: compatibles `actions,s500-timer`, `actions,s700-timer`, `actions,s900-timer`, named IRQ, CCF clock, OF mapping.

Risks: derived offsets must match SoC layout; clock is not explicitly prepared/enabled before `clk_get_rate()`; init error paths do not unmap; oneshot resume callback is a no-op. Test signals include named IRQ resolution, clocksource count, event compare interrupts, and PD acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-owl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-pistachio.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-pistachio.c

Purpose: Imagination Pistachio GPT clocksource-only driver using a general-purpose timer selected through peripheral syscon clock muxing.

Important APIs/types/functions: `struct pistachio_clocksource` wraps base, raw spinlock, and clocksource. `gpt_readl/writel()` calculate per-GPT offsets. `pistachio_clocksource_read_cycles()` reads overflow then current value in strict order under lock. `pistachio_clocksource_enable/disable()` program GPT0 reload/local enable.

Control flow: init maps GPT registers, gets peripheral regmap from `img,cr-periph`, switches timer control to fast clock, obtains and enables `sys` and `fast` clocks, disables IRQ masks for all GPTs, enables global timer block, initializes lock, registers sched_clock, then registers the clocksource.

State/persistence: static `pcs_gpt` stores all state. GPT0 local enable and reload value control the source. No clockevent state exists.

Dependencies/integration: compatible `img,pistachio-gptimer`, syscon regmap phandle, named clocks, clocksource/sched_clock.

Risks: no clockevent support; clocksource read depends on overflow-read latch semantics; failure paths after clock enable only partially unwind; `CLOCK_SOURCE_SUSPEND_NONSTOP` assumes timer continues through suspend. Test signals include regmap mux programming, fast clock rate, clocksource monotonicity, suspend behavior, and absence of GPT IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-pistachio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-probe.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-probe.c

Purpose: central early boot dispatcher for clocksource timer drivers registered in the `__timer_of_table` linker section and ACPI timer table.

Important APIs/types/functions: `timer_probe()` iterates `for_each_matching_node_and_match()` over `__timer_of_table`; `__timer_of_table_sentinel` marks section end. It treats `match->data` as `of_init_fn_1_ret` and also calls `acpi_probe_device_table(timer)`.

Control flow: for every matching DT node, skip unavailable nodes, call the registered init function, log failures except `-EPROBE_DEFER`, and count successful timers. Then add successful ACPI probes. If no timers were initialized, emit a critical log.

State/persistence: no driver-owned persistent state besides local count. It consumes linker-section registrations created by `TIMER_OF_DECLARE()` macros elsewhere.

Dependencies/integration: OF core, ACPI probe tables, clocksource header declarations, and architecture boot calling `timer_probe()`.

Risks: init functions must be idempotent or self-filter when multiple compatible nodes match; deferred probe is only skipped/log-suppressed here and not retried by this function itself; critical no-timer log is fatal for platform bring-up diagnosis. Test signals include correct linker table population, disabled DT nodes being skipped, ACPI timer discovery, and expected logs for missing/misconfigured timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-pxa.c

Purpose: Marvell/Intel PXA OS timer driver providing OSCR clocksource/sched_clock and OSMR0 one-shot clockevent for DT and legacy non-DT boards.

Important APIs/types/functions: global `timer_base`; `pxa_ost0_interrupt()` disarms OIER_E0, clears OSSR_M0, and dispatches. `pxa_osmr0_set_next_event()` writes match as OSCR plus delta and checks `MIN_OSCR_DELTA`. `pxa_timer_common_init()` registers shared clocksource/clockevent; `pxa_timer_nodt_init()` supports legacy boards.

Control flow: DT init maps shared timer/watchdog registers, gets/enables clock, parses IRQ0, then calls common init. Common init disables all timer IRQs, clears match status, registers sched_clock, requests IRQ, registers MMIO clocksource, and configures one-shot clockevent. PM suspend stores OSMR/OIER/OSCR and resume restores while ensuring OSMR0 is safely ahead.

State/persistence: global base plus optional PM save arrays persist. Clockevent is a static object. Registers are shared with watchdog channel/enable register.

Dependencies/integration: compatible `marvell,pxa-timer`, legacy `clk_get(NULL, "OSTIMER0")`, `<clocksource/pxa.h>`, PM hooks, sched_clock.

Risks: no periodic mode; shared watchdog registers; clocksource init failure after IRQ request does not free IRQ; resume writes OSCR which can affect monotonicity but adjusts match instead where needed. Test signals include min-delta `-ETIME` avoidance, suspend/resume wake tick, DT and non-DT init, and OSCR clocksource stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-qcom.c

Purpose: Qualcomm KPSS/SCSS timer driver using GPT0 for per-CPU or shared one-shot clockevents and CPU0 DGT as clocksource/sched_clock/delay.

Important APIs/types/functions: global `event_base`, `sts_base`, and `source_base`; per-CPU `msm_evt`; `msm_timer_set_next_event()` clears/programs match and waits for pending clear if status exists. `msm_timer_init()` allocates events, requests percpu IRQ when applicable, installs CPU hotplug, registers clocksource/sched_clock/delay.

Control flow: DT init maps event base, parses IRQ index 1, reads optional `cpu-offset`, maps CPU0 source base separately, reads `clock-frequency`, sets DGT div4, computes source/event bases and reduced frequency, then calls common init. CPU startup initializes each clockevent and either enables percpu IRQ or requests shared IRQ. ISR stops oneshot timer then dispatches.

State/persistence: global MMIO bases and IRQ metadata; per-CPU event allocation persists. Source timer is enabled even if event setup failed because common init proceeds through `err` label to clocksource registration.

Dependencies/integration: compatibles `qcom,kpss-timer` and `qcom,scss-timer`, DT `clock-frequency`/`cpu-offset`, CPU hotplug, percpu IRQ, ARM delay timer.

Risks: event setup errors still fall through to clocksource registration; shared IRQ request on every CPU startup may be inappropriate if not percpu; fixed GPT_HZ for events while source frequency is divided DT frequency; busy-wait on clear-pending status can hang on bad hardware. Tests include percpu and non-percpu DTs, CPU hotplug, match clear polling, and DGT clocksource frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ralink.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ralink.c

Purpose: Ralink RT3352/MT7620 system tick counter driver providing a 16-bit MMIO clocksource and a higher-rated one-shot clockevent.

Important APIs/types/functions: `struct systick_device` stores membase, clockevent, IRQ request flag, and scale. `systick_next_event()` programs compare modulo `SYSTICK_FREQ`. `systick_set_oneshot()` lazily requests IRQ and enables external systick routing/counter; `systick_shutdown()` frees IRQ and disables config.

Control flow: init maps MMIO, manually calculates clockevent mult/shift/delta bounds for fixed 50 kHz, parses IRQ, registers MMIO clocksource, then registers the clockevent device. The IRQ handler simply dispatches the event handler. Shutdown tears down the IRQ, so re-entering oneshot will request it again.

State/persistence: static `systick` object holds all driver state. `irq_requested` tracks dynamic IRQ ownership.

Dependencies/integration: compatible `ralink,cevt-systick`, fixed `SYSTICK_FREQ`, MIPS IRQ routing comment, clocksource/clockevents.

Risks: no explicit interrupt acknowledge in handler; dynamic request/free from clockevent state transitions can fail and still sets `irq_requested = 1`; modulo compare on 50k range limits deltas; typo comment aside, event handler default is a no-op until core replaces it. Tests should verify IRQ routing to MIPS IRQ7, oneshot reactivation, compare wrap, and source registration at rating 301.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ralink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rda.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rda.c

Purpose: RDA8810PL timer driver using OSTIMER as clockevent and 64-bit HWTIMER as clocksource/sched_clock.

Important APIs/types/functions: static `rda_ostimer_of` uses `timer-of` with named base `rda-timer` and named IRQ `ostimer`. `rda_ostimer_start/stop()` program load low/control high bits and IRQ mask. `rda_hwtimer_clocksource_read()` reads low then high with a high-stability loop. `rda_hwtimer_clocksource` is a 64-bit continuous source.

Control flow: init calls `timer_of_init()`, registers the HWTIMER clocksource at fixed 2 MHz, registers sched_clock, then registers OSTIMER clockevent. Periodic mode computes cycles per jiffy from clockevent mult/shift, starts repeat mode; next-event starts one-shot; ISR clears OSTIMER IRQ and dispatches if handler exists.

State/persistence: one static `timer_of`; clocksource read reuses the same base as OSTIMER. Hardware IRQ mask and control registers carry event mode.

Dependencies/integration: compatible `rda,8810pl-timer`, named DT resource/IRQ, fixed rate assumption, clocksource/clockevents/sched_clock.

Risks: rate is hard-coded rather than from DT clock; HWTIMER and OSTIMER share one mapped base; no clock resource; event min/max uses `UINT_MAX` though OSTIMER load has 56 bits. Tests include fixed-rate validation, 64-bit read ordering, named IRQ lookup, periodic and one-shot events, and suspend wake behavior if used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-realtek.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-realtek.c

Purpose: Realtek RTD1625 system timer clockevent driver using a 64-bit timestamp comparator. It does not register a clocksource.

Important APIs/types/functions: global `systimer_base`; `rtk_ts64_read()` reads low then high timestamp words; `rtk_cmp_value_write()` writes high/low compare value; `rtk_cmp_en_write()` toggles comparator with write-enable bit. `rtk_syst_clkevt_next_event()` programs current timestamp plus cycles. `rtk_ts_match_intr_handler()` disables comparator, clears status, and dispatches.

Control flow: init acquires base/IRQ through `timer_of_init()` and registers a dynamic one-shot clockevent at fixed 1 MHz with min delta 0x64. Shutdown disables comparator, clears compare value and pending status. One-shot state also routes to shutdown, so actual arming occurs only in `set_next_event()`.

State/persistence: static `rtk_timer_to` and global base persist. Comparator enable/value registers define runtime state.

Dependencies/integration: compatible `realtek,rtd1625-systimer`, `timer-of`, IRQ polling/timer flags, fixed timer rate.

Risks: no source registration means another clocksource must exist; low/high timestamp read lacks retry if high changes after low; fixed 1 MHz rate must match hardware; clear-status writes combine read status and clear bit. Test signals include one-shot comparator interrupts, min-delta behavior, correct status clearing, and coexistence with platform clocksource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-realtek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-riscv.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-riscv.c

Purpose: generic RISC-V timer driver for per-hart clockevents and global clocksource/sched_clock using the architectural time counter, SBI timer calls, or Sstc supervisor timer compare CSRs.

Important APIs/types/functions: static key `riscv_sstc_available` selects CSR compare programming versus `sbi_set_timer()`. Per-CPU `riscv_clock_event`; `riscv_clocksource`; `riscv_cs_get_mult_shift()` exports conversion parameters. `riscv_timer_init_common()` registers source, percpu IRQ, detects Sstc, and installs hotplug.

Control flow: DT init validates hartid/cpuid and only initializes common path on the boot CPU’s CPU node, also reading `riscv,timer-cannot-wake-cpu`. ACPI init reads RHCT wake flag. Common init maps `RV_IRQ_TIMER` through the interrupt controller domain, registers 64-bit clocksource and sched_clock, requests percpu IRQ, enables Sstc static branch if ISA extension exists, then sets CPU hotplug callbacks. CPU startup stops pending timer, sets features/rating, registers event, and enables IRQ. Interrupt stops timer and dispatches.

State/persistence: static clocksource and per-CPU event structures, global IRQ, static key, and wake capability flag.

Dependencies/integration: RISC-V arch timebase, IRQ domains, SBI, Sstc CSRs, DT/ACPI, CPU hotplug, VDSO clock mode.

Risks: relies on synchronized hart timers; 32-bit Sstc write ordering is critical; init is gated to one CPU node; cannot-wake flag affects deep idle. Tests include DT and ACPI boot, Sstc and SBI paths, CPU hotplug, exported mult/shift users, and timer interrupt after idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rockchip.c

Purpose: Rockchip RK3288/RK3399 timer driver assigning first matching timer node to clockevent and second to clocksource/sched_clock.

Important APIs/types/functions: `struct rk_timer` stores base/control pointer/clocks/frequency/IRQ; `struct rk_clkevt` embeds clockevent plus timer. `rk_timer_probe()` maps and enables clocks, selects control register offset by compatible, and parses IRQ. `rk_clkevt_init()` and `rk_clksrc_init()` build framework devices.

Control flow: `rk_timer_init()` checks global pointers: first call initializes event, second initializes source, further calls fail. Clockevent next/periodic disable, load counter low/high, then enable with user/free-running and interrupt flags. ISR clears status, disables oneshot, and dispatches. Clocksource init loads UINT_MAX, enables timer, registers down-counting MMIO source, and sched_clock.

State/persistence: global `rk_clkevt` and `rk_clksrc` pointers persist, with `ERR_PTR` used to prevent repeated init after failure. Source and event require separate hardware timer nodes.

Dependencies/integration: compatibles `rockchip,rk3288-timer` and `rockchip,rk3399-timer`, named `pclk` and `timer` clocks, DT IRQ, clocksource/clockevents.

Risks: DT node order determines role; first timer must be suitable for IRQ clockevent and second for source; cleanup does not release IRQ mapping; control register offset mismatch breaks RK3399. Test signals include two-node boot order, pclk/timer clock enable, down-count source, oneshot disable after ISR, and too-many-timers log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rtl-otto.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-rtl-otto.c

Purpose: Realtek Otto timer driver using the first N timers as per-CPU clockevents and the next timer as a stable 28-bit clocksource/sched_clock.

Important APIs/types/functions: per-CPU `timer_of rttm_to` requests base/clock/IRQ; `struct rttm_cs` wraps source `timer_of` and clocksource. Register helpers set period, mode, divisor, IRQ bits. `rttm_bounce_timer()` works around a late-stop/start hardware window. `rttm_probe()` initializes all timers and hotplug.

Control flow: probe loops possible CPUs, assigning base/IRQ index equal to CPU and initializing each event timer, then initializes clocksource at index `num_possible_cpus()`. It enables source in timer mode, registers clocksource/sched_clock, and installs CPU hotplug. CPU startup forces IRQ affinity, registers event at fixed 3.125 MHz, and enables IRQ. Event callbacks bounce/stop/program/restart in counter or timer mode; ISR acks and dispatches.

State/persistence: per-CPU static timer_of objects, global `rttm_cs`, fixed target tick rate, and hardware divisor derived from input clock. No dynamic teardown except rollback on early per-CPU init failure.

Dependencies/integration: compatible `realtek,otto-timer`, `timer-of`, CPU hotplug, per-CPU IRQs, IRQ affinity, CCF clock.

Risks: requires at least `num_possible_cpus()+1` timer resources; source init failure only logs and still installs hotplug; divisor calculation assumes clock rate supports 3.125 MHz; hardware workaround is timing-sensitive. Tests include resource-count DT validation, CPU hotplug/affinity, one-shot near min delta, source timer index, and monotonic 28-bit source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-rtl-otto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp.h -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp.h

Purpose: shared register definitions and small state structs for ARM SP804-style dual timers and Integrator variants.

Important APIs/types/functions: defines two timer base offsets, common register offsets, control bits for oneshot, 32-bit mode, divisors, interrupt enable, periodic, and enable. `struct sp804_timer` describes variant register layout and width, including HiSilicon 64-bit high-register offsets. `struct sp804_clkevt` stores resolved MMIO pointers and reload/width for a timer channel.

Control flow: none beyond data layout. `timer-sp804.c` and `timer-integrator-ap.c` consume the constants to program timer channels.

State/persistence: header-defined structs become caller-owned state. `NR_TIMERS` encodes the two-channel SP804 block assumption.

Dependencies/integration: used by SP804 and Integrator AP timer drivers; no standalone kernel registration.

Risks: constants annotate platform support in comments but no compile-time enforcement exists; mismatched variant width or offset tables can corrupt timer programming. Test signals are build coverage and runtime timer bring-up for ARM SP804, HiSilicon SP804, and Integrator platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp804.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp804.c

Purpose: ARM/HiSilicon SP804 dual-timer driver supporting clocksource/sched_clock/delay timer and clockevent roles, plus Integrator/CP two-node handling.

Important APIs/types/functions: variant descriptors `arm_sp804_timer` and `hisi_sp804_timer`; `sp804_clkevt` array resolves timer channel MMIO; `sp804_clocksource_and_sched_clock_init()` initializes a down-counting source; `sp804_clockevents_init()` initializes common event timer and IRQ; `sp804_of_init()` chooses timer1/timer2 roles based on `arm,sp804-has-irq`.

Control flow: common OF init skips after first device, maps base, disables both timers, obtains clocks, parses IRQ, initializes channel pointer table, then selects event/source channel. Source path loads all-ones, enables periodic mode, registers MMIO clocksource, optional delay timer, and sched_clock. Event path computes reload, requests IRQ, and registers clockevent. Integrator/CP path uses call count: first node source, second event.

State/persistence: static channel array, `common_clkevt`, `sched_clkevt`, delay pointers, and initialized/init_count gates. Event handling is global, so one event timer at a time.

Dependencies/integration: compatibles `arm,sp804`, `hisilicon,sp804`, `arm,integrator-cp-timer`, `timer-sp.h`, optional ARM delay, CCF clocks.

Risks: request_irq failure only logs but still registers clockevent; HiSilicon 64-bit descriptor still registers 32-bit source read; single-device gate ignores additional SP804s; clock selection with three parent clocks is subtle. Tests should cover role property, Integrator call count, clock rates, IRQ clear, and delay/sched_clock registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sp804.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sprd.c

Purpose: Spreadtrum timer driver with one clockevent timer and a separate suspend-nonstop 64-bit clocksource.

Important APIs/types/functions: static `timer_of to` for events and `suspend_to` for persistent source. Event helpers enable/disable/update counter/interrupt and callbacks implement periodic, shutdown, and next-event. `sprd_suspend_timer_read()` reads shadow high/low/high and inverts for a down-counter-style source.

Control flow: `sprd_timer_init()` initializes base/clock/IRQ, enables interrupt, and registers a periodic/oneshot dynamic clockevent. Interrupt clears flag, disables timer for oneshot, and dispatches. `sprd_suspend_timer_init()` initializes a base/clock-only timer and registers `suspend_clocksource`; enable loads max 64-bit value and starts periodic 64-bit mode.

State/persistence: two static `timer_of` structures and one static clocksource. The suspend timer can continue through suspend by clocksource flags.

Dependencies/integration: compatibles `sprd,sc9860-timer` and `sprd,sc9860-suspend-timer`, `timer-of`, clocksource/clockevents.

Risks: event `set_state_oneshot` is not explicitly supplied, relying on `set_next_event`; suspend source read assumes shadow register protocol; `sprd_timer_enable_interrupt()` writes only enable bit and may clear other status depending on hardware semantics. Test signals include both DT nodes, suspend clocksource selection, one-shot disable after interrupt, 64-bit shadow read consistency, and periodic events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32-lp.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32-lp.c

Purpose: STM32 low-power timer platform driver providing a high-rated clockevent from the MFD STM32 LPTIM block, with wakeup support.

Important APIs/types/functions: `struct stm32_lp_private` stores regmap, clockevent, period, prescaler, device, clock, and hardware version. `stm32_clkevent_lp_set_timer()` dispatches version-specific ARR/IER programming. `stm32mp25_clkevent_lp_set_evt()` handles newer synchronization flags. Probe uses parent MFD data.

Control flow: probe obtains parent `stm32_lptimer` regmap/clock/version, enables clock, checks rate, gets parent IRQ, optionally enables wake IRQ, requests IRQ, computes prescaler to target less than `32000 * HZ`, initializes and registers clockevent. Event programming writes ARR/IER, starts continuous or single mode. IRQ clears ARRM flag and dispatches. Suspend shuts down timer and disables clock; resume reenables clock and restores prescaler.

State/persistence: devm-allocated private struct lives with platform device. Prescaler and period are cached for resume and periodic mode.

Dependencies/integration: platform compatible `st,stm32-lptimer-timer`, STM32 LPTIM MFD parent, regmap, CCF clock, wakeirq PM helpers, module platform driver.

Risks: parent IRQ lookup uses parent platform device; version-specific polling timeout can fail in atomic context; high rating may select this low-power event broadly; wake-source handling must balance device wake state. Tests include STM32MP25 register-sync path, older path, wakeup-source suspend, prescaler calculation, and IRQ clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32-lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32.c

Purpose: STM32 general timer driver registering each compatible timer as a clocksource and clockevent, with sched_clock/delay only from the first 32-bit timer.

Important APIs/types/functions: `struct stm32_timer_private` stores detected width. `stm32_timer_set_width()` probes ARR truncation to detect 16/32 bits. `stm32_timer_set_prescaler()` targets 10 MHz for 16-bit timers and no prescale for 32-bit. Clockevent callbacks use CCR1 compare interrupts.

Control flow: init allocates `timer_of`, initializes base/clock/IRQ, allocates private data, optionally resets hardware, detects width, sets prescaler/rate/period, registers clocksource, then registers clockevent. Clocksource path starts a 32-bit timer immediately for sched_clock/delay if none exists. Next-event writes CNT+delta to CCR1 and returns `-ETIME` if already missed; IRQ clears status, reprograms periodic or shuts down oneshot, then dispatches.

State/persistence: each timer has heap `timer_of` and private width data. Global `stm32_timer_cnt` selects one sched_clock/delay counter.

Dependencies/integration: compatible `st,stm32-timer`, reset controller, `timer-of`, ARM delay timer, clocksource/clockevents.

Risks: `(1 << bits) - 1` overflows for 32-bit `int`; cleanup after private allocation failure calls `timer_of_cleanup()` but frees only outer `to`; periodic mode reprograms using current CNT after IRQ. Test signals include 16- and 32-bit timers, reset behavior, sched_clock only once, compare miss handling, and clockevent max delta correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun4i.c

Purpose: Allwinner A10/A23/V3s/Suniv timer driver using timer1 as down-counting clocksource and timer0 as clockevent.

Important APIs/types/functions: static `timer_of to`; helpers stop/setup/start timer channels and synchronize after disable by polling timer1 for `TIMER_SYNC_TICKS`. `sun4i_timer_sched_read()` reads inverted timer1. Clockevent callbacks implement shutdown, periodic, one-shot, and next-event.

Control flow: init acquires base/clock/IRQ through `timer_of_init()`, programs timer1 reload/value as free-running OSC24M source, conditionally registers sched_clock on older SoCs without better arch timer, registers down-counting clocksource, configures timer0 source, stops it, clears interrupt, registers clockevent, and enables timer0 IRQ. Next-event subtracts sync ticks from delta before programming.

State/persistence: one static `timer_of` and source timer1 state. Interrupt enable register persists event routing.

Dependencies/integration: multiple Allwinner compatibles, `timer-of`, machine compatibility checks for sched_clock, MMIO clocksource/clockevents.

Risks: sync polling depends on timer1 running at same effective frequency; `evt - TIMER_SYNC_TICKS` underflows if event is too small but min delta is set to sync ticks; fixed OSC24M mux programming may conflict with clock description. Tests include old/new SoC sched_clock behavior, min-delta boundaries, IRQ clear/enable, and clocksource down-count conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun4i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun5i.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun5i.c

Purpose: Allwinner high-speed timer platform driver for sun5i/sun7i, providing timer1 clocksource and timer0 clockevent with clock-rate notifier support.

Important APIs/types/functions: `struct sun5i_timer` stores base, clock, notifier, ticks-per-jiffy, clocksource, and clockevent. `sun5i_rate_cb()` unregisters/re-registers clocksource and updates event frequency around clock changes. Setup functions initialize source and event. Probe uses devm resources and optional reset.

Control flow: probe allocates state, maps MMIO, gets IRQ and enabled clock, validates rate, registers clock notifier, deasserts optional reset, sets up source, then event. Source loads timer1 with max and starts reload mode. Event enables timer0 IRQ, registers clockevent, then requests IRQ. Event callbacks stop/sync timer0, program interval low register, and start one-shot or periodic; ISR clears IRQ status and dispatches.

State/persistence: platform driver state is stored as drvdata and removed by unregistering clocksource. Clock notifier mutates framework registrations and `ticks_per_jiffy`.

Dependencies/integration: compatibles `allwinner,sun5i-a13-hstimer` and `allwinner,sun7i-a20-hstimer`, CCF notifier, reset controller, platform driver, clocksource/clockevents.

Risks: event interrupt is enabled before `devm_request_irq()`; clock-rate changes during active events can race with event programming; sync polling assumes timer1 running; remove only unregisters clocksource, relying on devm for IRQ/resources. Tests include rate-change notifier, reset deassert, min-delta underflow boundary, remove path, and one-shot/periodic events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun5i.c -->
