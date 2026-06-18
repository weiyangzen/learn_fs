# sources/distributed-fs/ceph-client/drivers/power/reset/qnap-poweroff.c

## Purpose
QNAP NAS microcontroller poweroff driver.

## Important APIs, Types, and Functions
UART/serial or platform command helpers, global poweroff command path, and platform probe.

## Control Flow
probe validates Orion/QNAP platform data and registers poweroff; callback sends the board-specific command sequence to the microcontroller controlling main power.

## State and Persistence Behavior
minimal driver state; the external microcontroller owns persistent power-control state.

## Dependencies and Integration Points
PLAT_ORION, platform data/firmware interface, legacy poweroff hook.

## Risks and Edge Cases
command protocol is board-specific and usually unacknowledged at final shutdown; wrong model can send ineffective commands.

## Test Signals
supported QNAP NAS shutdown, command failure logging, and absence on unsupported boards.
