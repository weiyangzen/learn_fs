<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h

## Purpose
This header defines Richtek RT4831 backlight binding constants for over-voltage protection level and LED channel enable masks.

## Important APIs, types, and functions
It exports OVP level values `RT4831_BLOVPLVL_17V`, `21V`, `25V`, and `29V`, plus channel bits `RT4831_BLED_CH1EN` through `RT4831_BLED_CH4EN` and aggregate `RT4831_BLED_ALLCHEN`.

## Control flow
Backlight DTS nodes use these constants in RT4831 properties. The RT4831 driver reads the resulting values and programs OVP and enabled current-sink channels.

## State and persistence
No state exists in the header. The DTB supplies persistent board policy, and the driver writes runtime chip registers during probe/resume.

## Dependencies and integration points
It integrates with RT4831 MFD/backlight support, LED string wiring, regulator/backlight power sequencing, and schema validation.

## Risks and test signals
Risks include selecting an unsafe OVP level for the panel string, enabling unwired channels, and assuming `ALLCHEN` is valid for every board. Test signals include DTS validation, backlight probe, brightness ramp tests, OVP fault testing, and channel-current measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h -->
