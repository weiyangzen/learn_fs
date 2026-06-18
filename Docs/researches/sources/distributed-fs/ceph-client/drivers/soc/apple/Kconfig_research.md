# sources/distributed-fs/ceph-client/drivers/soc/apple/Kconfig

## Purpose
This file defines Apple SoC support options for mailbox IPC, RTKit protocol support, SART DMA filtering, and hardware tunables.

## Important APIs, Types, And Functions
Symbols are `APPLE_MAILBOX`, `APPLE_RTKIT`, `APPLE_SART`, and `APPLE_TUNABLE`. `APPLE_RTKIT` depends on `APPLE_MAILBOX`; `APPLE_MAILBOX` depends on PM and 64-bit compile-test support; SART and tunable depend on Apple architecture or compile-test.

## Control Flow
The whole Apple menu is gated by `ARCH_APPLE || COMPILE_TEST`. Selecting options controls whether the corresponding module objects are built by the Apple Makefile.

## State, Persistence, And Dependencies
Configuration is persisted in `.config`. Dependencies model RTKit's mailbox requirement and platform/compile-test availability.

## Integration Points
Apple NVMe, display, and coprocessor client drivers rely on these support libraries when enabled.

## Risks
If RTKit clients can be enabled without `APPLE_RTKIT`, link or probe failures occur elsewhere. Keeping `APPLE_TUNABLE` tristate but promptless means only dependent drivers should select it.

## Test Signals
Run Apple defconfig and COMPILE_TEST builds, confirm dependency propagation, and verify `APPLE_RTKIT=m` pulls in mailbox availability.
