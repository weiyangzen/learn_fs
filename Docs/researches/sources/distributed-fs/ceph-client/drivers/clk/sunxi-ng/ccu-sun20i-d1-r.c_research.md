# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.c

## Purpose
`ccu-sun20i-d1-r.c` is the PRCM/R-domain CCU provider for Allwinner D1/R528/T113 systems. It describes the always-on/RTC-side bus clocks and resets for the reduced power-management clock block, then registers them with the shared sunxi-ng CCU framework.

The provider is small but important for low-power peripherals such as R timer, watchdog/timer domain, PPU, IR receiver, RTC bus, and CPU configuration bus.

## Important APIs, Types, And Functions
The file uses sunxi-ng descriptor macros and common types:

- `SUNXI_CCU_MP_DATA_WITH_MUX` defines `r-ahb` and `r-apb0` as M/P dividers with mux parents from firmware clocks `hosc`, `losc`, `iosc`, and `pll-periph`.
- `SUNXI_CCU_GATE_HWS` defines bus gates for `bus-r-timer`, `bus-r-twd`, `bus-r-ppu`, `bus-r-ir-rx`, `bus-r-rtc`, and `bus-r-cpucfg`.
- `SUNXI_CCU_MP_DATA_WITH_MUX_GATE` defines the functional `r-ir-rx` clock with `losc`/`hosc` parents, M/P dividers, mux, and gate.
- `sun20i_d1_r_ccu_clks[]`, `sun20i_d1_r_hw_clks`, `sun20i_d1_r_ccu_resets[]`, and `sun20i_d1_r_ccu_desc` provide the descriptor data consumed by `devm_sunxi_ccu_probe()`.
- `sun20i_d1_r_ccu_probe()` maps MMIO and registers the provider.

## Control Flow
The platform driver matches `allwinner,sun20i-d1-r-ccu`. Probe maps resource 0 with `devm_platform_ioremap_resource()` and immediately calls `devm_sunxi_ccu_probe()`. All runtime clock operations are handled by generic sunxi-ng ops for mux/divider/gate/reset descriptors.

Clock consumers request clock enable, disable, parent selection, or rate changes through CCF. Reset consumers assert/deassert reset IDs from the `dt-bindings/reset/sun20i-d1-r-ccu.h` namespace through the reset map.

## State And Persistence
There is no filesystem persistence. Runtime state is the PRCM RCC register contents: selected parents and divider values for `r-ahb`, `r-apb0`, and `r-ir-rx`, gate bits for R-domain peripherals, and reset bits for timer, TWD, PPU, IR RX, RTC, and CPUCFG. Firmware may initialize some always-on clocks before Linux.

The provider uses devm-managed registration, so software resources are tied to the platform device lifetime. The hardware register state persists only until reset or explicit reconfiguration.

## Dependencies And Integration Points
The driver depends on Linux platform device and module APIs, `clk-provider.h`, the sunxi-ng common framework (`ccu_common.h`, `ccu_reset.h`, `ccu_gate.h`, `ccu_mp.h`), and IDs from `ccu-sun20i-d1-r.h`.

Integration points include the D1/R528/T113 device tree node, PRCM/RTC-domain peripherals, remote/infrared input, RTC, timer/watchdog-related blocks, and reset-controller consumers. Parent clocks `hosc`, `losc`, `iosc`, and `pll-periph` must be available by firmware name.

## Risks
The main risk is incorrect R-domain parent or divider modeling. These clocks often remain active across low-power states, so wrong rates can affect wake timers, IR reception, RTC access, or CPU configuration paths. Reset bits share registers with gates at different bit positions; confusing bit 0 gate fields with bit 16 reset fields can leave devices stuck.

The provider has no custom sanity checks after MMIO mapping. Bad device-tree compatible or resource size issues will only surface through failed probe or later broken consumers.

## Test Signals
Expected signals are successful probe of `sun20i-d1-r-ccu`, populated clocks for `r-ahb`, `r-apb0`, and R-domain gates in `clk_summary`, and reset-controller entries for the six R-domain resets. Hardware tests should cover RTC access, R timer operation, IR receiver if present, suspend/resume wake behavior, and reset assertions for R-domain peripherals without disturbing the main CCU.
