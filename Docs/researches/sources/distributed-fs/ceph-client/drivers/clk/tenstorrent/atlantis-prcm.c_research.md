# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/atlantis-prcm.c

## Purpose

`atlantis-prcm.c` is the Tenstorrent Atlantis PRCM clock-controller driver. It registers CCF clocks for the RCPU clock domain, including PLLs, muxes, read-only dividers, gates, shared gates, and fixed-factor aliases. It also creates an auxiliary reset device for the same PRCM block.

## Important APIs, Types, And Functions

The driver defines register offsets for RCPU and NOCC PLL/config/gate registers and bitfields for PLL enable, bypass, dividers, feedback divider, lock detect, and lock status. `struct atlantis_clk_common` embeds `clk_hw`, an integer clock ID, and a regmap pointer shared by all custom clock types. Specialized wrappers model muxes, gates, dividers, PLLs, shared gates, and fixed factors.

Clock operations include `atlantis_clk_mux_get_parent()`/`set_parent()`, `atlantis_clk_gate_enable()`/`disable()`/`is_enabled()`, `atlantis_clk_divider_recalc_rate()`, `atlantis_clk_fixed_factor_recalc_rate()`, and `atlantis_clk_pll_enable()`/`disable()`/`recalc_rate()`/`is_enabled()`. Shared gates use `refcnt_qspi`, `refcnt_can0`, and `refcnt_can1` protected by `refcount_lock` so paired functional and bus clocks manipulate one hardware gate bit.

The macro layer (`ATLANTIS_PLL_DEFINE`, `ATLANTIS_MUX_DEFINE`, `ATLANTIS_DIVIDER_DEFINE`, `ATLANTIS_GATE_DEFINE`, `ATLANTIS_GATE_SHARED_DEFINE`, `ATLANTIS_FIXED_FACTOR_DEFINE`) instantiates the clock topology. `atlantis_prcm_clocks_register()` registers all `clk_hw`s and publishes a onecell provider. `atlantis_prcm_probe()` maps MMIO, initializes regmap, registers clocks, and creates the reset auxiliary device.

## Control Flow

The platform driver matches `tenstorrent,atlantis-prcm-rcpu`. Probe maps resource 0 with `devm_platform_ioremap_resource()`, wraps it in a 32-bit MMIO regmap, gets match data, and registers every clock in `atlantis_rcpu_clks`. During registration, each static clock object's `common.regmap` is assigned and its ID indexes the provider array. After clock registration, `devm_auxiliary_device_create()` creates a reset child named by `reset_name`.

Runtime PLL enable first forces bypass, toggles the enable register bit low then high, polls the PLL config register for `PLL_CFG_LOCK_BIT`, clears bypass, and optionally enables an output gate. Disable switches to bypass and powers down the PLL. Rate recalculation returns the parent rate in bypass and otherwise computes `parent * fbdiv / (refdiv * postdiv1 * postdiv2)`, normalizing zero divisors to one except for zero `fbdiv`.

## State And Persistence Behavior

The driver has static clock descriptors and static shared-gate reference counters. Hardware register state persists across CCF operations: PLL bypass and enable bits, mux selectors, divider fields, and gate bits. The shared-gate counters are in-memory only and represent Linux's view of paired consumers, not hardware state after reboot or firmware changes. The regmap uses `REGCACHE_NONE`, so reads and writes go directly to MMIO.

## Dependencies And Integration Points

The driver depends on CCF, regmap MMIO, platform devices, auxiliary bus, and DT binding IDs from `tenstorrent,atlantis-prcm-rcpu.h`. It integrates with device tree through `of_clk_hw_onecell_get`. Reset support is delegated to an auxiliary device, so a matching auxiliary reset driver is expected elsewhere.

## Risks And Edge Cases

The PLL enable path assumes the lock bit appears within `PLL_LOCK_TIMEOUT_US`; slow silicon or incorrect reference clocks can fail probe-time or runtime enables. Optional PLL output gates are represented by `cg_reg_enable`; for `rcpu_pll_clk` this is zero and the final update writes a zero mask, which should be harmless but relies on regmap semantics. Shared gate reference counts can become inconsistent if CCF disables unused clocks without matching prior enables; the custom `disable_unused` only clears hardware when the counter is zero. Divider clocks implement recalc only, so consumers cannot program divider fields through CCF.

## Test Signals

Build with `CONFIG_TENSTORRENT_ATLANTIS_PRCM` built-in and as a module. Boot an Atlantis DT with `tenstorrent,atlantis-prcm-rcpu`, verify the clock provider registers all binding IDs, and inspect `clk_summary` for RCPU, NOCC, LSIO, QSPI, CAN, UART, SPI, I2C, GPIO, timer, watchdog, security, and fixed-factor clocks. Exercise shared QSPI and CAN clocks with multiple consumers and verify the shared gate stays enabled until the last consumer disables it. Validate PLL rates against register fields and confirm the auxiliary reset device binds.
