<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h

## Purpose
This header defines charge-pump mode constants for TI/National LP55xx LED controller device-tree bindings.

## Important APIs, types, and functions
It exports `LP55XX_CP_OFF`, `LP55XX_CP_BYPASS`, `LP55XX_CP_BOOST`, and `LP55XX_CP_AUTO`.

## Control flow
LP55xx DTS nodes use these values in charge-pump configuration properties. The driver reads the numeric property and programs the chip's charge-pump behavior.

## State and persistence
The header has no state. The chosen mode persists as board configuration in the DTB and then as runtime chip register state after probe.

## Dependencies and integration points
It integrates with LP5521/LP5523/LP5562-style LED controller drivers and their device-tree schemas.

## Risks and test signals
Risks include selecting a mode unsupported by a specific chip or board power design, causing brightness/current issues. Test signals include `dtbs_check`, LP55xx probe, LED brightness tests, and power/current validation under boost and bypass modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h -->
