<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h

## Purpose
Declares RZ-family USBHS platform-info exports.

## Important APIs, Types, And Functions
Declares `usbhs_rza1_plat_info`, `usbhs_rza2_plat_info`, and `usbhs_rzg2l_plat_info`.

## Control Flow
No runtime flow. `common.c` selects these symbols via compatible match data; `rza.c` and `rza2.c` define them.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `common.h` and bridges common match data to RZ-family glue.

## Risks
Some declared symbols are defined in `rza2.c`, not `rza.c`; Makefile linkage must include both. Declaration mismatch breaks OF match builds.

## Test Signals
Build RZ/A1, RZ/A2, and RZ/G2L match paths and verify symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h -->
