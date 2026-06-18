<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h

## Purpose
This header defines mode constants for LaCie/Seagate Netxbig LED device-tree bindings.

## Important APIs, types, and functions
It exports `NETXBIG_LED_OFF`, `NETXBIG_LED_ON`, `NETXBIG_LED_SATA`, `NETXBIG_LED_TIMER1`, and `NETXBIG_LED_TIMER2`.

## Control flow
Board DTS files use the constants to describe LED mode wiring or default behavior. The Netxbig LED driver converts the numeric mode into hardware control behavior.

## State and persistence
There is no header state. Mode choices persist in DTB data and become runtime LED state after driver probe.

## Dependencies and integration points
It integrates with the Netxbig LED driver, SATA activity indication, timer blink logic, and board-specific LED GPIO/register wiring.

## Risks and test signals
Risks include mismatching SATA/timer modes with physical LED wiring and using board-specific values outside the driver contract. Test signals include DTS validation, LED on/off tests, SATA activity indication, and timer blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h -->
