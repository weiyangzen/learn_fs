<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h

## Purpose
Declares R-Car Gen3 USBHS platform-info exports.

## Important APIs, Types, And Functions
Declares `usbhs_rcar_gen3_plat_info` and `usbhs_rcar_gen3_with_pll_plat_info`.

## Control Flow
No runtime flow; `common.c` references symbols and `rcar3.c` defines them.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `common.h` and connects Gen3 match data to platform glue.

## Risks
Declaration mismatch breaks Gen3 compatible linkage.

## Test Signals
Build Gen3 compatible paths and verify both symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h -->
