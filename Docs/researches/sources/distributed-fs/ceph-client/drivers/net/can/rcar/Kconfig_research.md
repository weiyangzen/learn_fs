# sources/distributed-fs/ceph-client/drivers/net/can/rcar/Kconfig

## Purpose
This Kconfig file defines Renesas R-Car/RZ-G CAN controller build options.

## Important APIs, Types, And Functions
- `CAN_RCAR` enables the classic Renesas R-Car and RZ/G CAN controller driver.
- `CAN_RCAR_CANFD` enables the Renesas R-Car CAN FD controller driver.
- Both depend on `ARCH_RENESAS || COMPILE_TEST`.

## Control Flow
The two options are independent tristates. Selecting each causes the corresponding object to be built by the local Makefile.

## State And Persistence
Only build-time configuration is represented.

## Dependencies And Integration Points
The dependency allows native Renesas builds and compile-test coverage elsewhere. The CAN FD help notes that the FD driver runs the controller in CAN FD only mode while interoperating with CAN 2.0 nodes.

## Risks And Edge Cases
- Users expecting a dedicated classic CAN 2.0 mode from `CAN_RCAR_CANFD` may be surprised; the help explicitly says FD-only controller mode.
- Runtime dependencies such as clocks, resets, IRQs, and device-tree bindings are not expressed in this Kconfig fragment.

## Test Signals
Check build visibility under Renesas and COMPILE_TEST configs, and verify module names `rcar_can` and `rcar_canfd`.
