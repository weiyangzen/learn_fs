<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c

## Purpose
Provides legacy platform-data initialization for Nokia N800/N810/N810 WiMAX OMAP2420 boards, covering TUSB6010 USB, SPI WLAN, Menelaus PMIC, MMC slot multiplexing/power, and GPIO lookup tables.

## Important APIs, Types, and Functions
Key entry points are `n8x0_legacy_init()` and `omap_late_initcall n8x0_late_initcall()`. Important helpers include `board_check_revision()`, `n8x0_usb_init()`, MMC power/bus/cover callbacks, Menelaus late-init voltage/sleep setup, and callback registration.

## Control Flow
Legacy init identifies the board by DT compatible, registers SPI board info, and returns MMC platform data. Late init initializes MMC slot data, TUSB6010 USB interface, and ASoC GPIO lookups. MMC late init programs Menelaus slot selection, power rails, slot modes, initial cover state, and card-change callback. Power callbacks route slot 0 through Menelaus on all boards and slot 1 through Menelaus or GPIO depending on N800/N810.

## State and Persistence Behavior
Static state includes `board_caps`, cover-open flags, `mmc_device`, `mmc1_data`, GPIO lookup tables, Menelaus platform data, and board SPI info. Hardware state includes PMIC regulators, MMC slot muxing, GPIO power controls, and TUSB6010 interface setup.

## Dependencies and Integration Points
Depends on Menelaus MFD APIs, OMAP MMC platform data, GPIO lookup tables, TUSB6010 setup, MUSB platform data, SPI board registration, and DT machine compatible checks.

## Risks
Board variant detection drives slot naming and power behavior; a wrong compatible can power the wrong rail. Menelaus callbacks can `BUG()` on unexpected MMC voltage or bus mode. Cover-state bits are inverted until first switch change and handled specially.

## Test Signals
Boot N800, N810, and N810 WiMAX DTs; verify board_caps, SPI p54spi registration, TUSB6010 enumeration, MMC slot power/cover events, Menelaus regulator sleep setup, and N810 internal MoviNAND `ban_openended` behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-n8x0.c -->
