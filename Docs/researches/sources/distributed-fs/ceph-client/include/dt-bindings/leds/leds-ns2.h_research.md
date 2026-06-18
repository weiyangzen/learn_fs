<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h

## Purpose
This header defines simple LED mode constants for Network Space v2 LED bindings.

## Important APIs, types, and functions
It exports `NS_V2_LED_OFF`, `NS_V2_LED_ON`, and `NS_V2_LED_SATA`.

## Control flow
DTS nodes use these constants in board LED mode properties. The NS2 LED driver maps the numeric value to off, steady on, or SATA activity behavior.

## State and persistence
The file has no state. DTB values persist as board configuration and driver-programmed LED behavior.

## Dependencies and integration points
It integrates with NS2 board LED support and storage activity indication.

## Risks and test signals
Risks include assigning SATA mode to a LED not wired for activity and confusing this board-specific binding with generic LED function strings. Test signals include LED mode smoke tests and SATA activity indication during I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h -->
