# sources/distributed-fs/ceph-client/drivers/power/reset/ltc2952-poweroff.c

## Purpose
LTC2952 PowerPath controller poweroff and watchdog/trigger driver.

## Important APIs, Types, and Functions
state structure with trigger/kill GPIOs and watchdog timer, IRQ/work handlers, and sys-off poweroff callback.

## Control Flow
probe obtains GPIOs/IRQ and timing properties, arms watchdog handling, and registers poweroff; external trigger events initiate orderly shutdown while poweroff asserts kill after required delays.

## State and Persistence Behavior
software timers/work track trigger and watchdog timing; GPIO levels persist into final powerdown.

## Dependencies and Integration Points
OF, GPIO descriptors, IRQ, timers/workqueues, sys-off poweroff.

## Risks and Edge Cases
timing properties must match the external controller; missed trigger IRQs or kill polarity errors can power-cycle unexpectedly; concurrent watchdog/work and shutdown paths need ordering.

## Test Signals
trigger IRQ, watchdog timeout, kill pulse timing, active-low GPIOs, suspend interaction, and board poweroff.
