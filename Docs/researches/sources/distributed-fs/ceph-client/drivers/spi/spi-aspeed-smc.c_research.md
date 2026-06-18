# sources/distributed-fs/ceph-client/drivers/spi/spi-aspeed-smc.c

## Purpose
ASPEED FMC/SPI memory controller driver for SPI NOR style devices across AST2400, AST2500, AST2600, and AST2700 variants. It provides `spi-mem` exec and direct-map read support, user-mode SPI transfers, AHB window management, chip enable/type setup, and read timing calibration.

## Important APIs, Types, and Functions
`struct aspeed_spi_data` describes per-SoC capabilities, segment encoding, clock dividers, calibration, max CS, and window granularity. `struct aspeed_spi` is controller-wide state; `struct aspeed_spi_chip` stores per-CS control registers, AHB mapping, configured read controls, clock, and forced user-mode flag. Important paths include `aspeed_spi_exec_mem_op()`, `aspeed_spi_dirmap_create()`, `aspeed_spi_dirmap_read()`, `aspeed_spi_setup()`, `aspeed_spi_user_transfer()`, `aspeed_spi_set_window()`, adjustment helpers, and calibration helpers.

## Control Flow
Probe selects SoC data from OF, maps controller registers and the AHB memory resource, enables the clock, configures controller callbacks, computes default windows, and registers the controller. Setup initializes per-CS registers, optionally sets flash type, and enables the chip. `exec_op` programs opcode, address mode, dummy cycles, data width, and user-mode read/write helpers, then restores default read control state. Direct-map creation adjusts the AHB segment window to the requested flash range, programs command-mode read settings, sets 3-byte or 4-byte address mode, and calibrates read timing. Direct-map reads use `memcpy_fromio()` when the window covers the request, otherwise fall back to user-mode command reads.

## State and Persistence
Per-chip `ctl_val[]` caches base/read/write control values and calibrated dividers. Segment registers persist remapped AHB windows. `force_user_mode` persists when trimming makes command mode incomplete. `cs_change` tracks user transfer preparation/unpreparation.

## Dependencies and Integration Points
It integrates with SPI core and `spi_mem`, platform OF data, clk, MMIO, and memory resources. It matches ASPEED FMC/SPI compatibles and relies on child nodes to determine active chip selects.

## Risks
Window calculations are hardware-specific and can reduce command-mode coverage, affecting performance and debug behavior. Calibration requires non-uniform flash data; uniform regions force low speed. Some user-mode full-duplex support is AST2700-specific and rejects dual/quad full-duplex. No DMA path is implemented even though IRQ comments mention DMA. Address-mode changes are global CE control bits and must be restored correctly.

## Test Signals
Run SPI NOR read/write/erase via `spi-mem`, direct-map reads across window edges, 3-byte and 4-byte address modes, dual/quad read modes, multi-CS window layouts, calibration logs at different flash contents, fallback-to-user-mode reads, and remove-time chip disable checks.
