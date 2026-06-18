<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h

## Purpose
Declares the R-Car Gen2 USBHS platform-info symbol.

## Important APIs, Types, And Functions
Declares `extern const struct renesas_usbhs_platform_info usbhs_rcar_gen2_plat_info;`.

## Control Flow
No runtime flow; `common.c` references the symbol and `rcar2.c` defines it.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `common.h` and connects OF match data to Gen2 glue.

## Risks
Symbol declaration mismatch breaks linkage.

## Test Signals
Build Gen2 compatible paths and verify symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h -->
