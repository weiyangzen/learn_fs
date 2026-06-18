# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s3c64xx-clock.h

## Purpose
`samsung,s3c64xx-clock.h` defines stable clock IDs for Samsung S3C64xx DT-enabled platforms. Its comments explicitly mark the IDs as ABI and require additions only in free spaces or at the end.

## Important APIs, types, and functions
The header exports core clocks (`CLK27M`, `CLK48M`, `FOUT_*`, `ARMCLK`, `HCLKX2`, `HCLK`, `PCLK`), HCLK/PCLK bus gates, `SCLK_*` special clocks, S3C6410-specific `MEM0_*` clocks, `MOUT_*` muxes, `DOUT_*` dividers, and `NR_CLKS`. There are intentional gaps between groups to preserve ABI.

## Control flow
There is no executable flow. Device trees use the IDs in clock phandles; the S3C64xx clock driver maps them to Samsung clock framework entries.

## State and persistence
The file has no state. Numeric IDs are persistent ABI and especially sensitive because the header documents non-renumbering rules. Runtime state is in S3C64xx clock registers.

## Dependencies and integration points
It integrates with S3C64xx/S3C6410 DTS files, Samsung clock drivers, bus/peripheral drivers, display, camera, USB host, SD/MMC, audio, UART, SPI, I2C, IrDA, scaler, and memory-bus clock users.

## Risks and test signals
Risks include filling gaps incorrectly, changing `NR_CLKS`, or applying S3C6410-specific MEM0 IDs to incompatible SoCs. Test signals include DT compilation, clock provider registering all expected IDs, boot console, USB/storage/display/audio peripheral tests, and clk-summary validation of mux/divider/gate relationships.
