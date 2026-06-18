# subset-b-001191 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra.c

## Purpose

`timer-tegra.c` is the legacy NVIDIA Tegra clocksource and per-CPU clockevent driver for Tegra20-era through Tegra210 timer blocks, plus a suspend-nonstop RTC clocksource. It programs the timer microsecond counter to 1 MHz, registers `timer_us` as the sched clock and generic clocksource, and creates per-CPU clockevent devices backed by timer instances and DT IRQs. Tegra20/Tegra30 get a high rating because the local TWD timer is affected by CPU DVFS jitter; Tegra210 also prefers this timer because the architected timer cannot survive some CPU power/reset events.

## Important APIs, Types, And Functions

The key state is `usec_config`, `timer_reg_base`, the per-CPU `struct timer_of tegra_to`, and `suspend_rtc_to`. `tegra_init_timer()` is the common initializer used by `TIMER_OF_DECLARE()` entries for `nvidia,tegra210-timer` and `nvidia,tegra20-timer`. `tegra_timer_set_next_event()`, `tegra_timer_shutdown()`, `tegra_timer_set_periodic()`, and `tegra_timer_isr()` implement the clockevent callbacks. `tegra_timer_setup()` and `tegra_timer_stop()` are CPU hotplug callbacks registered at `CPUHP_AP_TEGRA_TIMER_STARTING`. `tegra_read_sched_clock()` and `clocksource_mmio_init()` expose the free-running 1 us counter. `tegra20_init_rtc()` registers `tegra_suspend_timer` from the RTC millisecond/seconds registers.

## Control Flow

Early OF timer matching calls the SoC-specific wrapper, which calls `timer_of_init()`, stores the base, selects a supported parent-clock divider value for `TIMERUS_USEC_CFG`, and writes it. It then iterates over all possible CPUs, computes the timer register base and IRQ index, maps each IRQ, sets IRQ no-auto-enable, requests the timer IRQ, and stores per-CPU clockevent metadata. After IRQ setup, it registers sched_clock, the `timer_us` MMIO clocksource, the optional ARM delay timer, and a CPU hotplug state. Each CPU startup clears PTV/PCR, forces IRQ affinity, enables the IRQ, and registers the local clockevent. Interrupts clear `TIMER_PCR_INTR_CLR` and call the event handler.

## State And Persistence Behavior

Hardware register state carries the persistent timer programming. The driver saves only the computed microsecond divider in `usec_config`; clockevent resume rewrites it because the register can be lost across suspend. Per-CPU event state lives in static per-CPU `timer_of` objects. The RTC clocksource is separate and marked `CLOCK_SOURCE_SUSPEND_NONSTOP`; its reader relies on the shadow seconds register and warns that it must not race the full RTC driver.

## Dependencies And Integration Points

It depends on OF address/IRQ parsing, `timer-of`, clocksource/clockevents, CPU hotplug, sched_clock, cpumasks, and ARM delay timer registration. Device-tree compatibility strings and IRQ ordering are part of the ABI. The driver integrates with platform power behavior by selecting ratings that compete with TWD or arch timers.

## Risks And Test Signals

Risks include unsupported parent clock rates returning `-EINVAL`, wrong DT IRQ ordering breaking per-CPU events, the timer n+1 programming convention causing off-by-one changes, and RTC shadow-register races. Test by booting matching Tegra DTS files, checking `timer_us` and `tegra_timer` in clocksource/clockevent logs, hotplugging CPUs, suspending/resuming, and verifying sched_clock monotonicity and interrupt affinity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra186.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra186.c

## Purpose

`timer-tegra186.c` is a platform driver for Tegra186 and Tegra234 timer-controller blocks. It registers three continuous clocksources from shared TKE registers (`tsc`, `osc`, and `usec`) and exposes watchdog 0 through the Linux watchdog framework using a preconfigured timer as the watchdog source. Unlike `timer-tegra.c`, it does not provide Linux clockevents; its runtime device model is a removable platform driver with suspend/resume hooks.

## Important APIs, Types, And Functions

`struct tegra186_timer_soc` describes timer/watchdog counts per SoC. `struct tegra186_timer` stores the MMIO base, device, SoC data, watchdog, and three `struct clocksource` objects. `struct tegra186_tmr` and `struct tegra186_wdt` model per-timer and watchdog register windows. `tegra186_wdt_create()` builds a watchdog, detects locked configuration via `WDTCR_LOCAL_INT_ENABLE`, reads its timer source, creates that timer, initializes min/max/default timeout, and registers it with `devm_watchdog_register_device()`. Watchdog ops are `start`, `stop`, `ping`, `set_timeout`, and `get_timeleft`. Clocksource initializers register fixed-rate TSC at 31.25 MHz, OSC at 38.4 MHz, and USEC at 1 MHz.

## Control Flow

Probe allocates `tegra186_timer`, loads OF match data, maps resource 0, obtains IRQ 0 as a basic DT validation step, creates watchdog 0, then registers the three clocksources. Failure after TSC registration unwinds previously registered clocksources. Remove unregisters usec, osc, and tsc. Suspend disables the watchdog if active; resume re-enables it.

The watchdog enable path unmasks the hardware IRQ in `TKEIE()`, clears the timer interrupt, selects the microsecond source, programs a periodic timer for one fifth of the requested timeout, optionally writes WDTCR fields when not locked, then starts the watchdog counter. A reset occurs on the fifth expiration. `get_timeleft()` combines the current 29-bit down-counter value with the remaining expiration count and rounds microseconds to seconds.

## State And Persistence Behavior

Persistent state is mostly hardware-backed: WDTCR may be locked by firmware, timer source selection can be preconfigured, and TKE clocksources are free-running registers. The driver stores watchdog timeout and active state in watchdog core fields and rewrites watchdog/timer registers on ping, timeout change, and resume. If WDTCR is locked, only timer programming and counter command writes are changed.

## Dependencies And Integration Points

The driver uses platform devices, OF match data, `devm_platform_ioremap_resource()`, watchdog core, clocksource core, PM ops, and MMIO helpers. It integrates with DT compatibles `nvidia,tegra186-timer` and `nvidia,tegra234-timer`, and with the watchdog device node exposed by the timer block.

## Risks And Test Signals

Risks include fixed-rate assumptions for TSC/OSC/USEC, incorrect timer/window offsets when SoC timer counts change, overflow or rounding mistakes in `get_timeleft()`, and locked firmware watchdog configuration limiting reprogramming. Test by loading on Tegra186/Tegra234, verifying all three clocksources register and unregister cleanly, using `/dev/watchdog` start/ping/timeout/timeleft paths, suspending with an active watchdog, and checking that reset occurs near the requested timeout only when pings stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-32k.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-32k.c

## Purpose

`timer-ti-32k.c` registers the OMAP/TI 32 kHz synchronized counter as a low-power continuous clocksource and sched_clock. This counter is preferred on many OMAP-class systems because it is always available and survives low-power modes better than higher-frequency general-purpose timers.

## Important APIs, Types, And Functions

`struct ti_32k` stores the MMIO base, selected counter register address, and `struct clocksource`. `ti_32k_read_cycles()` reads the selected 32-bit counter. `omap_32k_read_sched_clock()` adapts it for sched_clock. `ti_32k_timer_module_init()` handles nodes whose parent is `ti,sysc` by enabling parent `fck` and optional `ick` clocks, then forcing the module into idle-friendly state. `ti_32k_timer_init()` maps registers, selects the correct counter offset by inspecting revision scheme bits, registers the clocksource at 32768 Hz, and registers sched_clock. `TIMER_OF_DECLARE()` binds `ti,omap-counter32k`.

## Control Flow

During early timer initialization, the driver maps the node, marks the clocksource as suspend-nonstop except on AM43, initializes parent module clocks when needed, and determines whether the counter register uses the legacy low offset (`0x10`) or highlander high offset (`0x30`). It then registers `32k_counter` and sched_clock. There are no interrupts or clockevents.

## State And Persistence Behavior

The state is static and global: `ti_32k_timer` holds the mapping and clocksource for the lifetime of the kernel. Register programming is minimal; this driver enables clocks and may write the parent sysconfig register to force idle. The free-running counter itself is hardware-owned.

## Dependencies And Integration Points

It depends on OF address mapping, OF clock lookup on the parent module, common clock prepare/enable, clocksource, sched_clock, and `ti,sysc` parent conventions. The system-timer DMTimer code detects this node to decide whether a DMTimer clocksource is needed, so this file indirectly affects TI timer selection policy.

## Risks And Test Signals

Risks include misdetecting the revision offset, missing parent clocks, treating AM43 as suspend-nonstop when it is not, and leaving `ti,sysc` clock handling inconsistent with normal platform probing. Test by booting OMAP/TI boards with `ti,omap-counter32k`, checking the log for `32k_counter at 32768 Hz`, confirming sched_clock registration, validating suspend/resume timekeeping, and checking that DMTimer clocksource selection changes when the 32 kHz counter is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-32k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm-systimer.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm-systimer.c

## Purpose

`timer-ti-dm-systimer.c` is the early-boot system timer driver for TI OMAP/AM/DM dual-mode timers. It selects suitable DMTimer instances from device tree, configures one as a clockevent and optionally one as a clocksource, supports AM33xx/AM43 idle handling, and adds a DRA7 per-CPU timer workaround for ARM architected timer erratum i940.

## Important APIs, Types, And Functions

`struct dmtimer_systimer` stores an MMIO base, revision-dependent register offsets, clocks, and rate. `struct dmtimer_clockevent` wraps a clockevent plus timer state and periodic load value. `struct dmtimer_clocksource` wraps a clocksource plus timer state and saved load value. Selection globals are `counter_32k`, `clocksource`, and `clockevent`. Core helpers include revision detection, type1/type2 reset, `dmtimer_systimer_setup()`, `dmtimer_systimer_select_best()`, `dmtimer_clockevent_init()`, `dmtimer_clocksource_init()`, and `dmtimer_percpu_quirk_init()`.

## Control Flow

The first matched timer calls `dmtimer_systimer_select_best()`. Selection detects whether `ti,omap-counter32k` exists, finds preferred DT timers requiring parent `ti,no-reset-on-init`, `ti,no-idle`, assigned clock parents for non-secure timers, and no DSP/PWM role, then chooses an always-on timer for clockevent or clocksource depending on 32 kHz counter availability. Quirks force OMAP3 Beagle AB4 and AM43 behavior. The matching timer node is then initialized as clockevent, clocksource, DRA7 per-CPU timer, or ignored.

Clockevent setup maps and resets the timer, enables clocks, sets posted mode for clockevent use, requests IRQ, enables overflow/wakeup interrupts, and registers periodic/oneshot callbacks. `set_next_event()` writes counter to `0xffffffff - cycles` and starts the timer after pending-write waits. Periodic mode programs load/counter then starts autoreload. Clocksource setup starts an autoreload free-running timer, optionally installs AM43 suspend/resume callbacks, registers sched_clock from the first counter, and registers the clocksource.

## State And Persistence Behavior

The chosen physical addresses persist in static globals to keep later TIMER_OF callbacks from reselecting. Each clockevent/clocksource allocation persists for the kernel lifetime. On AM33xx/AM43, clockevent idle callbacks disable/enable the functional clock and restore interrupt/wakeup enables. AM43 clocksource suspend saves the counter, disables the timer clock, and resumes by restoring the counter and autoreload start bits.

## Dependencies And Integration Points

It depends on `clocksource/timer-ti-dm.h` register definitions, `dt-bindings/bus/ti-sysc.h`, OF node scanning, `ti,sysc` parent properties, assigned-clock defaults, common clocks, CPU hotplug, clockevents, clocksource, sched_clock, and TI machine compatible quirks.

## Risks And Test Signals

Risks include DT property omissions causing no system timer selection, selecting DSP/PWM timers needed by other drivers, wrong revision offsets, unbounded pending-write loops, erratum handling regressions, and AM43/OMAP3 quirks changing timekeeping. Test by booting OMAP2/3/4/5, AM33xx, AM43, DM814/816, and DRA7 DTs; inspect selected physical addresses; exercise periodic and oneshot ticks, CPU hotplug on DRA7, suspend/resume on AM33xx/AM43, and operation with and without the 32 kHz counter node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm-systimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm.c

## Purpose

`timer-ti-dm.c` is the runtime platform driver and exported API provider for TI OMAP dual-mode timers. It exposes request/free/control operations through `struct omap_dm_timer_ops` in platform data so PWM, remoteproc, and legacy users can reserve timers, configure clock sources, enable interrupts, run counters, configure PWM/capture modes, and read/write status/counter registers. It is distinct from the early system timer driver but shares hardware definitions.

## Important APIs, Types, And Functions

`struct dmtimer` is the central state object: it embeds an `omap_dm_timer` cookie, IRQ, functional clock, revision-specific register bases, posted-write state, reservation flag, saved context, capabilities, errata flags, runtime-PM notifiers, and list node. `dmtimer_read()` and `dmtimer_write()` enforce posted-write pending checks encoded in register constants. `_omap_dm_timer_request()` implements reservation by any timer, ID, capability, or DT node. Public ops include request variants, `free`, `enable`, `disable`, `set_source`, `start`, `stop`, `set_load`, `set_match`, `set_pwm`, `set_prescaler`, interrupt enable/disable, status/counter read/write, capture configuration, and capture read.

## Control Flow

Probe obtains match/platform data, IRQ and MMIO resource, parses DT capability flags (`ti,timer-alwon`, `ti,timer-dsp`, `ti,timer-pwm`, `ti,timer-secure`), gets and tracks the functional clock for non-OMAP1 devices, registers CPU PM notifier for non-always-on timers, enables runtime PM, initializes registers for unreserved timers, clears control state, and appends the timer to the global list under `dm_timer_lock`.

When a client requests a timer, the global list is scanned under spinlock and a matching unreserved timer is marked reserved. `omap_dm_timer_prepare()` runtime-resumes the device, optionally resets OMAP1-style timers, enables posted mode unless errata i103/i767 requires non-posted mode, and drops runtime PM. Most control operations runtime-resume the device around register access, write the relevant fields, update saved context when needed, then put runtime PM.

## State And Persistence Behavior

Reservation state is in `timer->reserved` and `omap_timer_list`. Runtime availability is tracked by `atomic_t enabled`. Register context is saved on runtime suspend and CPU cluster PM enter for non-always-on enabled timers, then restored on resume/exit. Functional clock rate is tracked by a clock notifier so stop delays match clock changes. Errata i103/i767 disables posted mode because reading counters after posted writes is unsafe.

## Dependencies And Integration Points

The driver integrates with platform bus, OF matching (`ti,omap*`, `ti,am335x*`, `ti,dm816`, `ti,am654`), runtime PM, common clock framework, CPU PM, OMAP1 IO/idlect code, `clocksource/timer-ti-dm.h`, and `linux/platform_data/dmtimer-omap.h`. It supplies timer operations to other kernel drivers rather than user space directly.

## Risks And Test Signals

Risks include incorrect posted/non-posted handling, reservation races, missing runtime PM references around register IO, context loss across CPU cluster suspend, wrong capability matching causing clients to get system timers, and capture/PWM mode side effects. Test with clients requesting timers by node/capability, PWM output, interrupt enable/disable, counter reads/writes on errata SoCs, runtime suspend/resume, CPU cluster PM, clock-rate changes, and removal while timers are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-ti-dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-versatile.c

## Purpose

`timer-versatile.c` is a minimal sched_clock driver for ARM Versatile and Versatile Express system-register blocks. It maps the sysreg node, reads the 24 MHz counter at offset `SYS_24MHZ`, and registers it as a 32-bit sched_clock source. It does not register a clocksource or clockevent.

## Important APIs, Types, And Functions

The sole persistent pointer is `versatile_sys_24mhz`. `versatile_sys_24mhz_read()` returns the current counter value with `readl()`. `versatile_sched_clock_init()` maps the DT resource with `of_iomap()`, clears `OF_POPULATED` on the node so other sysreg users can still bind, stores the counter address, and calls `sched_clock_register(..., 32, 24000000)`. `TIMER_OF_DECLARE()` binds `arm,vexpress-sysreg` and `arm,versatile-sysreg`.

## Control Flow

Early OF timer init invokes the initializer for matching sysreg nodes. If mapping fails, it returns `-ENXIO`; otherwise sched_clock registration completes and the mapping remains for kernel lifetime.

## State And Persistence Behavior

State is read-only except for the saved MMIO pointer. The hardware counter is assumed free-running and 32-bit. There is no suspend/resume or cleanup path.

## Dependencies And Integration Points

It depends on OF address mapping, sched_clock, MMIO, and the sysreg DT compatible. Clearing `OF_POPULATED` is an integration detail that allows a later regular sysreg/platform driver to coexist with this early timer hook.

## Risks And Test Signals

Risks are limited but include wrong offset assumptions, mapping failure, wrap behavior at 24 MHz, and conflicts if clearing `OF_POPULATED` is removed. Test by booting vexpress/versatile DTs, checking sched_clock source registration, confirming the sysreg device can still probe later, and validating monotonic timestamps across early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-vt8500.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-vt8500.c

## Purpose

`timer-vt8500.c` is the VIA/WonderMedia VT8500 timer driver. It registers a 3 MHz MMIO clocksource and a one-shot clockevent using a single global timer register block. It supports the `via,vt8500-timer` DT compatible through early `TIMER_OF_DECLARE()`.

## Important APIs, Types, And Functions

Global `regbase` stores the mapped timer registers. `vt8500_timer_read()` triggers a counter read, waits for the access-status bit to clear with a bounded loop, and returns `TIMER_COUNT_VAL`. `vt8500_timer_set_next_event()` computes an absolute match from the clocksource plus delta, waits for match-write readiness, writes the match value, rejects too-near deadlines using `MIN_OSCR_DELTA`, then enables the interrupt. `vt8500_shutdown()` disables interrupt delivery. `vt8500_timer_interrupt()` clears all status bits and calls the clockevent handler.

## Control Flow

Initialization maps MMIO, maps IRQ 0, enables/reset-clears the timer, sets the match register to all ones, registers the clocksource at `VT8500_TIMER_HZ`, requests the IRQ with timer/irqpoll flags, sets the clockevent cpumask to CPU0, and registers the one-shot clockevent with a minimum delta of twice the hardware guard.

## State And Persistence Behavior

The driver keeps no dynamic software state beyond the global base and static clocksource/clockevent objects. Hardware match, count, interrupt enable, status, and control registers define active behavior. There is no suspend/resume or hotplug path; the clockevent is CPU0-oriented.

## Dependencies And Integration Points

It depends on OF address/IRQ parsing, clocksource, clockevents, IRQ handling, delay calibration (`loops_per_jiffy`), and MMIO. The clockevent and clocksource share the same underlying counter and global state.

## Risks And Test Signals

Risks include access-status loops timing out silently, near-deadline `-ETIME` behavior under interrupt latency, lack of SMP/per-CPU handling, no cleanup after partial init failures, and assumed 3 MHz fixed rate. Test by booting a VT8500 DT, checking clocksource/clockevent registration, running high-resolution timer workloads, testing nonblocking near-deadline behavior through clockevents, and validating no spurious interrupts after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-zevio.c -->
# sources/distributed-fs/ceph-client/drivers/clocksource/timer-zevio.c

## Purpose

`timer-zevio.c` supports LSI Zevio timer blocks. It creates a one-shot clockevent from timer1 when an interrupt register block and IRQ are present, and always creates a 16-bit free-running clocksource from timer2. The driver can handle multiple DT timer nodes by deriving unique names from the resource start address and node name.

## Important APIs, Types, And Functions

`struct zevio_timer` stores base mappings for timer1, timer2, interrupt registers, the clock, embedded `clock_event_device`, and generated names. `zevio_timer_set_event()` loads a down-counter delta and starts timer1 in decrement-to-match mode. `zevio_timer_shutdown()` disables interrupts, acknowledges pending bits, and stops timer1. `zevio_timer_set_oneshot()` enables the match interrupt and clears pending bits. `zevio_timer_interrupt()` verifies the match bit, acks it, stops timer1, and calls the event handler. `zevio_timer_add()` performs mapping, clock lookup, optional IRQ setup, clockevent registration, timer2 free-run programming, and `clocksource_mmio_init()`.

## Control Flow

Early OF matching calls `zevio_timer_init()`, which delegates to `zevio_timer_add()`. The function allocates permanent state, maps resource 0, gets clock 0, maps optional interrupt resource 1, maps IRQ 0, constructs names, conditionally initializes the clockevent, then initializes timer2 as an incrementing forever-running counter with divider 0 and registers it as a 16-bit up-counting MMIO clocksource.

## State And Persistence Behavior

Allocated timer state is intentionally not freed on success because early timer drivers persist for the kernel lifetime. Hardware state includes timer1 interrupt mask/control/current value and timer2 control/current/divider registers. The source clock rate is queried dynamically at init, but the driver does not track later rate changes.

## Dependencies And Integration Points

It depends on OF address/IRQ/clock lookup, clockevents, clocksource MMIO helpers, IRQ handling, and slab allocation. The optional clockevent path allows a node without interrupt resources to still provide a clocksource.

## Risks And Test Signals

Risks include a failed `request_irq()` still allowing clockevent registration, optional interrupt mapping leaks on error paths, only 16-bit clocksource width, missing clock-rate-change handling, and no suspend/resume. Test with DT nodes with and without interrupt resources, verify unique clocksource/clockevent names, run oneshot timer workloads, inspect interrupt ack behavior, and check monotonicity around 16-bit wraps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clocksource/timer-zevio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/comedi/Kconfig

## Purpose

`drivers/comedi/Kconfig` defines the build-time configuration surface for the COMEDI data acquisition subsystem. It gates the core module, default asynchronous buffer sizes, bus-family menus, hardware driver modules, shared helper modules, and COMEDI-specific unit tests.

## Important APIs, Types, And Functions

The top-level `menuconfig COMEDI` enables the subsystem. `COMEDI_DEBUG` adds `-DDEBUG` through the Makefile. `COMEDI_DEFAULT_BUF_SIZE_KB` and `COMEDI_DEFAULT_BUF_MAXSIZE_KB` become defaults consumed by `comedi_fops.c` module parameters. Bus menus include `COMEDI_MISC_DRIVERS`, `COMEDI_ISA_DRIVERS`, `COMEDI_PCI_DRIVERS`, `COMEDI_PCMCIA_DRIVERS`, and `COMEDI_USB_DRIVERS`. Shared hidden/helper configs include `COMEDI_8254`, `COMEDI_8255`, `COMEDI_KCOMEDILIB`, `COMEDI_ISADMA`, `COMEDI_MITE`, `COMEDI_NI_TIO`, `COMEDI_NI_TIOCMD`, and `COMEDI_NI_ROUTING`.

## Control Flow

Kconfig visibility follows the top-level `if COMEDI`. Each bus menu controls whether the related driver prompts are shown, while `depends on` clauses enforce architecture/bus requirements such as PCI, PCMCIA, USB, HAS_IOPORT, HAS_DMA, HAS_IOMEM, ISA, PC104, X86_32, and COMPILE_TEST. Individual drivers `select` shared helper libraries needed at link time.

## State And Persistence Behavior

This file has no runtime state, but it determines compiled objects, module names, debug behavior, and the default values embedded into the COMEDI core. User-chosen tristate values persist in kernel configuration and affect module availability.

## Dependencies And Integration Points

It integrates with `drivers/comedi/Makefile` and subordinate driver Makefiles. The selected helper configs must match actual object exports used by bus and board drivers. Buffer-size defaults are mirrored by `CONFIG_COMEDI_DEFAULT_BUF_*` references in `comedi_fops.c`.

## Risks And Test Signals

Risks include missing `select` lines causing link failures, over-broad `select` lines forcing unsupported dependencies, missing `depends on HAS_IOPORT/HAS_DMA` for drivers that require those APIs, and stale module names in help text. Test with allmodconfig, allyesconfig, randconfig across PCI/USB/PCMCIA/ISA-disabled targets, and specific COMEDI_TESTS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/comedi/Makefile

## Purpose

`drivers/comedi/Makefile` maps COMEDI Kconfig symbols to core and bus support objects. It builds the core `comedi` module, optional `/proc` support, bus bridge modules, and recurses into helper and low-level driver directories.

## Important APIs, Types, And Functions

`ccflags-$(CONFIG_COMEDI_DEBUG) := -DDEBUG` turns the Kconfig debug option into compiler behavior. `comedi-y` defines the core aggregate objects: `comedi_fops.o`, `range.o`, `drivers.o`, and `comedi_buf.o`; `proc.o` is added when `CONFIG_PROC_FS` is enabled. `obj-$(CONFIG_COMEDI_PCI_DRIVERS)`, `obj-$(CONFIG_COMEDI_PCMCIA_DRIVERS)`, and `obj-$(CONFIG_COMEDI_USB_DRIVERS)` build bus helper modules. `obj-$(CONFIG_COMEDI)` builds the core and descends into `kcomedilib/` and `drivers/`.

## Control Flow

Kbuild evaluates the selected config symbols and links built-in or modular objects accordingly. The core object aggregation controls which files become part of the `comedi` module. Bus helper modules are separate from low-level board drivers.

## State And Persistence Behavior

There is no runtime state. Build output persists as built-in code or loadable modules according to Kconfig tristates.

## Dependencies And Integration Points

It depends on Kconfig symbols from `Kconfig` and on object files in the COMEDI directory. It integrates the core with `kcomedilib` and board-driver subdirectories by recursive `obj-$(CONFIG_COMEDI)` entries.

## Risks And Test Signals

Risks include omitting a core object from `comedi-y`, compiling bus helpers without their Kconfig dependencies, or debug flags unexpectedly affecting all COMEDI compilation. Test by building `COMEDI=m`, `COMEDI=y`, with and without `PROC_FS`, and with each bus menu as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_buf.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_buf.c

## Purpose

`comedi_buf.c` implements the COMEDI asynchronous data buffer. It allocates page-backed or DMA-coherent ring buffers, tracks mmap lifetime, supports producer/consumer reservation and release, performs optional sample munging, and exports helper APIs for low-level drivers and file operations.

## Important APIs, Types, And Functions

The main object is `struct comedi_buf_map`, refcounted by `kref` and containing a `page_list`, DMA direction, page count, and optional DMA hardware device reference. `comedi_buf_alloc()` resizes buffers under `dev->mutex`. `comedi_buf_map_from_subdev_get()`, `comedi_buf_map_access()`, `comedi_buf_is_mmapped()`, `comedi_buf_map_get()`, and `comedi_buf_map_put()` support mmap and VM access. Producer APIs include `comedi_buf_write_alloc()`, `comedi_buf_write_free()`, and `comedi_buf_write_samples()`. Consumer APIs include `comedi_buf_read_n_available()`, `comedi_buf_read_alloc()`, `comedi_buf_read_free()`, and `comedi_buf_read_samples()`.

## Control Flow

Allocation rounds requested size to pages, frees any old map, then allocates each page either with `dma_alloc_coherent()` or `get_zeroed_page()` plus `SetPageReserved()`. Freeing swaps `async->buf_map` to NULL under the subdevice spinlock, then drops the map ref; final release frees pages, clears PageReserved for non-DMA pages, releases the hardware device, and frees metadata. Ring operations adjust monotonic counts and modulo pointers. Write-free munges newly written bytes before readers see them. Sample helpers clamp to full sample counts, flag overflow, copy across page boundaries, update scan progress, and set `COMEDI_CB_BLOCK`.

## State And Persistence Behavior

Persistent buffer state is in `struct comedi_async`: preallocated size, counters, pointers, scan progress, munge state, and event flags. Counts are monotonic unsigned values; pointers wrap within `prealloc_bufsz`. Memory barriers enforce ordering between count updates and data visibility. Map refs keep pages alive while mmapped even if the subdevice buffer pointer changes.

## Dependencies And Integration Points

The file depends on `linux/comedi/comedidev.h`, DMA APIs, vmalloc/slab, page reservation, spinlocks, krefs, and COMEDI run-state helpers from `comedi_fops.c`. File operations use these helpers for read/write/mmap; low-level drivers use exported buffer APIs from interrupt or acquisition paths.

## Risks And Test Signals

Risks include resizing while mmapped or busy, DMA allocation without `CONFIG_HAS_DMA`, barrier regressions causing stale samples, partial-sample munging, page-boundary copy errors, and overflow event handling. Test with read and write async commands, mmap plus resize attempts, DMA and non-DMA subdevices, munge and raw-data modes, buffer wraparound, producer overflow, and concurrent close/cancel while buffer refs remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_fops.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_fops.c

## Purpose

`comedi_fops.c` is the COMEDI core character-device implementation. It owns board and subdevice minor allocation, open/close lifetime, ioctl dispatch, asynchronous command setup and cancellation, read/write/poll/mmap behavior, compat ioctl translation, event delivery, sysfs buffer attributes, and module initialization.

## Important APIs, Types, And Functions

`struct comedi_file` stores per-open device and selected read/write subdevices. Global minor tables map 0-255 minors to board or subdevice objects. `comedi_dev_put()` and internal `comedi_dev_get()` manage `struct comedi_device` krefs. Runflag helpers manage `COMEDI_SRF_RUNNING`, `BUSY`, `ERROR`, and private-data auto-free. Ioctl handlers include `do_devconfig_ioctl()`, `do_bufconfig_ioctl()`, `do_devinfo_ioctl()`, `do_subdinfo_ioctl()`, `do_chaninfo_ioctl()`, `do_bufinfo_ioctl()`, `do_insnlist_ioctl()`, `do_insn_ioctl()`, `do_cmd_ioctl()`, `do_cmdtest_ioctl()`, lock/unlock/cancel/poll, and subdevice selection handlers. File operations are collected in `comedi_fops`.

## Control Flow

`comedi_init()` registers the fixed COMEDI major region, cdev, class, optional legacy minors, and proc support. `open()` resolves a minor, allocates per-file state, enforces CAP_SYS_ADMIN for unattached devices, takes the low-level driver module on first open, calls driver `open()`, increments use count, and snapshots read/write subdevices. `close()` cancels commands owned by the file, releases locks, calls driver `close()` on last use, drops the module and device refs.

Ioctls mostly run under `dev->mutex`, except `COMEDI_BUFINFO`, read, write, poll, and mmap use `attach_lock` to protect against detach without serializing all buffer IO. `COMEDI_CMD` validates command and chanlist, runs `do_cmdtest`, resets buffer state, initializes `run_active`, sets runflags, marks `s->busy = file`, and calls low-level `do_cmd()`. `read()` and `write()` block on async wait queues, copy through `comedi_buf` helpers, honor nonblocking/signals, return `-EPIPE` on error completion, and transition to non-busy after stopped commands. `comedi_event()` is intended to process interrupt-set event flags, wake waiters, and send SIGIO.

## State And Persistence Behavior

Runtime state spans global minor tables, device krefs/use counts, per-file selected subdevices, subdevice locks/busy owner, async runflags, buffer counters, wait queues, fasync queues, sysfs buffer limits, and module parameters `comedi_num_legacy_minors`, `comedi_default_buf_size_kb`, and `comedi_default_buf_maxsize_kb`. Detach uses `detach_count` and `attach_lock` to detect stale subdevice pointers.

## Dependencies And Integration Points

It depends on char devices, device class/sysfs, uaccess, poll, mmap VM ops, fasync, compat ioctls, capabilities, COMEDI low-level driver callbacks, buffer helpers, range/chanlist validation, proc support, and module registration. Low-level drivers enter through `comedi_event()`, command callbacks, instruction callbacks, attach/detach, open/close, and buffer-change hooks.

## Risks And Test Signals

Risks include user-copy bounds mistakes, detach races, mmap lifetime leaks, deadlocks between `attach_lock` and `dev->mutex`, run_active completion misuse, ioctl ABI regressions, compat pointer translation errors, and event recursion/notification bugs in the observed source. Test with 32-bit and native ioctl suites, async read/write commands, command-test correction paths, mmap access and partial mapping failure, poll/SIGIO, subdevice minors, detach while IO is blocked, CAP_SYS_ADMIN gating, and module unload after open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_internal.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_internal.h

## Purpose

`comedi_internal.h` is the private header shared by COMEDI core files. It forward-declares core structures and exposes internal functions across `comedi_fops.c`, `comedi_buf.c`, `drivers.c`, `range.c`, and optional `proc.c` without making them public kernel APIs.

## Important APIs, Types, And Functions

It declares range ioctl handling, board and subdevice minor allocation/free, hardware-device release, buffer allocation/reset/map helpers, internal buffer reservation helpers, scan-progress and event helpers, device cancel/detach/attach functions, subdevice private auto-free checks, default buffer-size globals, global COMEDI driver list and lock, and `insn_inval()`. When `CONFIG_PROC_FS` is disabled, `comedi_proc_init()` and `comedi_proc_cleanup()` become no-op inline functions.

## Control Flow

There is no executable control flow beyond the `CONFIG_PROC_FS` conditional. The header defines compile-time visibility and call contracts for the core implementation files.

## State And Persistence Behavior

The header owns no state directly, but it declares persistent globals such as `comedi_default_buf_size_kb`, `comedi_default_buf_maxsize_kb`, `comedi_drivers`, and `comedi_drivers_list_lock`.

## Dependencies And Integration Points

It depends on compiler and type headers and intentionally uses forward declarations to avoid pulling full COMEDI definitions into every core file. It is the boundary between internal COMEDI components and exported headers under `linux/comedi/`.

## Risks And Test Signals

Risks include accidentally exposing private helpers to low-level drivers, stale prototypes after function signature changes, missing no-op stubs when optional features are off, and mismatched internal/external locking expectations. Test by building COMEDI with and without `PROC_FS`, with sparse/prototype warnings enabled, and by ensuring no external module includes this private header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_pci.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/comedi_pci.c

## Purpose

`comedi_pci.c` is the COMEDI PCI bus helper module. It provides common helper functions for PCI-backed COMEDI low-level drivers: PCI device lookup, enable/disable, generic detach cleanup, auto-config/unconfig wrappers, and combined COMEDI/PCI driver registration.

## Important APIs, Types, And Functions

`comedi_to_pci_dev()` converts `dev->hw_dev` to `struct pci_dev`. `comedi_pci_enable()` calls `pci_enable_device()`, requests BAR regions with `dev->board_name`, and sets `dev->ioenabled`. `comedi_pci_disable()` releases regions and disables the PCI device if enabled. `comedi_pci_detach()` frees `dev->irq`, unmaps `dev->mmio`, and disables PCI. `comedi_pci_auto_config()` and `comedi_pci_auto_unconfig()` bridge PCI probe/remove to COMEDI auto attach/detach. `comedi_pci_driver_register()` and `_unregister()` register or unwind COMEDI and PCI drivers in the correct order.

## Control Flow

A low-level PCI COMEDI driver typically calls the module helper macro backed by `comedi_pci_driver_register()`. PCI probe calls `comedi_pci_auto_config()`, whose COMEDI attach path lets the low-level driver recover the PCI device via `comedi_to_pci_dev()`. During detach or remove, generic cleanup may free IRQ/MMIO and disable the PCI device; auto unconfig ignores already-unconfigured devices through the COMEDI core.

## State And Persistence Behavior

The helper modifies `dev->ioenabled`, `dev->irq`, and `dev->mmio`. PCI enable state and requested regions persist until disabled. No private module state is stored.

## Dependencies And Integration Points

It depends on PCI APIs, module exports, interrupts, and `linux/comedi/comedi_pci.h`. It integrates COMEDI driver registration with the PCI driver core and is selected by `COMEDI_PCI_DRIVERS`.

## Risks And Test Signals

Risks include nested enable/disable misuse, failing to clear `ioenabled`, missing IRQ/MMIO cleanup in drivers that need extra resources, registration unwind ordering, and `hw_dev` not being a PCI device. Test with PCI COMEDI driver probe/remove, failed `pci_request_regions()`, failed `pci_register_driver()` unwind, manual detach before PCI remove, and repeated module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/comedi_pci.c -->
