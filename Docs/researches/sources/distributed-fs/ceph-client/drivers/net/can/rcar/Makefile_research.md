# sources/distributed-fs/ceph-client/drivers/net/can/rcar/Makefile

## Purpose
This Makefile maps Renesas R-Car CAN Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_RCAR) += rcar_can.o` builds the classic CAN driver.
- `obj-$(CONFIG_CAN_RCAR_CANFD) += rcar_canfd.o` builds the CAN FD driver.

## Control Flow
Kbuild includes each object independently according to its Kconfig symbol.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The file is paired with `rcar/Kconfig` and relies on driver source files outside this subset for actual implementation.

## Risks And Edge Cases
- There is no composite-object logic, so any shared helper code between `rcar_can.o` and `rcar_canfd.o` would need to live elsewhere or be duplicated.

## Test Signals
Build each option independently and together to verify object inclusion and module names.
