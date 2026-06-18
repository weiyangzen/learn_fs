# sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c

### Purpose
`tcu.c` implements common clock framework support for Ingenic Timer/Counter Unit clocks. It exposes timer channels, watchdog, and optional OST clocks as onecell `clk_hw` providers with selectable parents, prescalers, and stop-bit gates.

### Important APIs, Types, And Functions
Important types are `ingenic_soc_info`, `ingenic_tcu_clk_info`, `ingenic_tcu_clk`, and `ingenic_tcu`. Clock ops include enable/disable/is_enabled, get/set parent, recalc/determine/set rate. Setup functions are `ingenic_tcu_register_clock()`, `ingenic_tcu_probe()`, and `ingenic_tcu_init()`, registered for several `ingenic,*-tcu` compatibles.

### Control Flow, State, And Persistence
Probe obtains a regmap from the TCU syscon node, optionally gets/enables the parent `tcu` clock, allocates a fixed-size onecell provider, resets each channel TCSR to a default parent, registers channel clocks, registers watchdog with RTC as default parent, optionally registers OST, and adds the OF provider. Register access is gated by temporarily clearing stop bits because TCSR registers are only accessible when a channel is running. Syscore suspend disables the TCU parent clock and resume re-enables it.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on MFD syscon/regmap, `linux/mfd/ingenic-tcu.h`, common clock framework, clockchips, DT bindings, and CGU-provided parent clocks named `pclk`, `rtc`, `ext`, and sometimes `tcu`. Risks include global singleton state, legacy X1000 DTs missing the TCU clock, WARN-only regmap errors still returning success, cleanup index mistakes on partial registration, and parent mask interpretation via `ffs()`. Test signals include timer/watchdog clock lookup, parent switching, prescale rate rounding, boot with old X1000 DT, suspend/resume, and clocksource/watchdog operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/tcu.c -->
