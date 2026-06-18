# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.c

## Purpose
This helper exposes the Allwinner ADDA analog codec PRCM access register as a normal Linux regmap. The analog codec controls are not directly memory-mapped; reads and writes are tunneled through address, data-in, data-out, reset, and write-strobe fields in one 32-bit `ADDA_PR` register.

## Important APIs, types, and functions
`adda_reg_read()` and `adda_reg_write()` implement regmap bus callbacks over `readl()`/`writel()`. `adda_pr_regmap_cfg` defines 5-bit register addresses, 8-bit values, stride 1, `fast_io`, and `max_register = 31`. `sun8i_adda_pr_regmap_init()` is the exported API used by the analog codec driver to create a devm-managed regmap with the MMIO base as callback context.

## Control flow
Reads deassert ADDA reset, clear write mode, program the 5-bit analog register address into `ADDA_PR_ADDR`, then return the low 8-bit data-out field. Writes deassert reset, program the address, program the 8-bit data-in field, pulse `ADDA_PR_WRITE`, and clear the write bit. Initialization is a thin wrapper around `devm_regmap_init()`.

## State and persistence
The shim has no private state beyond the MMIO base pointer passed as regmap context. It does not use a software cache and relies on the consumer regmap/device lifecycle. Every access deasserts the analog reset bit, so access itself can bring the analog register bridge out of reset.

## Dependencies and integration points
It depends on MMIO accessors, regmap callback mode, and the declaration in `sun8i-adda-pr-regmap.h`. `sun8i-codec-analog.c` consumes this helper to register ASoC controls for the analog codec block. The symbol is exported GPL for other in-tree Allwinner analog codec users.

## Risks and edge cases
The read/write helpers perform read-modify-write sequences without explicit locking beyond whatever regmap serializes, so direct external access to the same PRCM register would be unsafe. There is no timeout or posted-write readback around the write strobe. Address and data are masked down to hardware width, so out-of-range values are silently truncated by the callback path after regmap's register limit checks.

## Test signals
Probe an analog codec user and verify regmap debugfs shows 5-bit registers. Exercise ALSA controls that span multiple analog registers, confirm writes pulse `ADDA_PR_WRITE`, and test suspend/resume or reset scenarios where each access must deassert `ADDA_PR_RESET`.
