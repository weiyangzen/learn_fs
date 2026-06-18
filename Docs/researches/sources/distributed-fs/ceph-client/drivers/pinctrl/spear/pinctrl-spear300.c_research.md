<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c

## Purpose
This file is the SPEAr300-specific overlay on top of the common SPEAr3xx pinmux tables. It adds SPEAr300 board/application modes, extra peripheral groups, and the `st,spear300-pinmux` platform driver.

## Important APIs, Types, And Data
- `PMX_CONFIG_REG` is the main mux register and `MODE_CONFIG_REG` selects one of the SPEAr300 mode encodings.
- `struct spear_pmx_mode` instances map mode names such as NAND, NOR, photo frame, IP phone, WiFi phone, ATA/PABX, and camera/LCD modes to 4-bit mode values.
- SPEAr300-specific functions include `fsmc`, `clcd`, `tdm`, `i2c1`, `cam`, `dac`, `i2s`, `sdhci`, and `gpio1`, in addition to `SPEAR3XX_COMMON_FUNCTIONS`.
- Each group has one or more `spear_modemux` entries with `.modes` masks so the common core can apply only the register writes valid for the active SoC mode.

## Control Flow And Integration
Probe fills the shared `spear3xx_machdata` with SPEAr300 group/function arrays, disables `gpio_pingroups`, enables mode support, attaches `spear300_pmx_modes`, initializes common group register addresses to `PMX_CONFIG_REG`, and delegates to `spear_pinctrl_probe()`.

Mux selection is mode-sensitive. For example, FSMC chip-select groups are available in NAND/NOR/photo-frame/ATA modes, CLCD groups differ between LCD and photo-frame modes, and camera, I2S, DAC, SDHCI, and GPIO1 groups are enabled only in selected mode combinations. Most SPEAr300 alternate functions are selected by clearing bits in `PMX_CONFIG_REG` that the common SPEAr3xx table otherwise uses for base functions.

## State And Persistence
Static tables are immutable. Hardware state persists in `PMX_CONFIG_REG` and `MODE_CONFIG_REG` after the common core writes the selected mode and pin group mux values. Unlike SPEAr310/320, this probe clears `gpio_pingroups`, so this file does not expose the common 3xx GPIO fallback table through `spear3xx_machdata`.

## Dependencies
It depends on `pinctrl-spear3xx.h` for common pins, groups, functions, mux masks, and shared `spear3xx_machdata`. It relies on `pmx_init_addr()` to rewrite common group mux register placeholders and on the common core to interpret `.modes`.

## Risks And Review Notes
- The group name `i2c_clk_grp_grp` does not match the function group string `i2c_clk_grp`; this looks like a functional lookup risk.
- Mode masks are dense and overlapping. A missing mode bit can make a valid board mode unable to select its peripheral pins.
- Many groups actively clear common 3xx mux bits; this can conflict with common functions if DT selects incompatible states.
- Because `gpio_pingroups` is set to `NULL`, GPIO fallback behavior differs from the other SPEAr3xx variants.

## Test Signals
Build SPEAr300 support and boot a DT with `st,spear300-pinmux`. Validate that the configured mode is written to `MODE_CONFIG_REG`, all expected groups appear in debugfs, and DT states for FSMC, CLCD, TDM, camera, I2S, DAC, SDHCI, and GPIO1 resolve. A targeted test should check the suspected `i2c1` group-name mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c -->
