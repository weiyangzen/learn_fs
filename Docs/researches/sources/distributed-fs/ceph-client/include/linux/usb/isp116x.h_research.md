# `sources/distributed-fs/ceph-client/include/linux/usb/isp116x.h`

## Purpose

`isp116x.h` defines platform data for the Philips/NXP ISP116x USB host controller driver. Board code uses it to describe electrical and timing quirks for platform-bus devices.

## Important APIs, Types, and Constants

- `struct isp116x_platform_data` exposes flags for internal downstream pull-down resistors, on-chip overcurrent detection, interrupt polarity, interrupt trigger mode, and remote wakeup.
- `delay(struct device *dev, int delay)` is a board-provided callback for strict inter-I/O timing between register accesses.

## Control Flow and Lifetimes

Platform setup attaches this structure to the device before driver probe. The ISP116x driver reads the flags during initialization and calls `delay()` around register accesses when the board requires precise bus timing. The data must outlive probe and normal driver operation.

## State and Persistence Behavior

The structure is static platform configuration. It does not store mutable runtime state, but selected flags affect controller power, interrupt, and wakeup behavior for the lifetime of the device.

## Dependencies and Integration Points

It integrates board initialization code, platform bus registration, and the ISP116x host controller driver. It references `struct device` in the delay callback.

## Risks and Edge Cases

Incorrect interrupt polarity or edge/level selection can lose interrupts. Omitting required I/O delays can corrupt register access. Remote wakeup increases suspend power because clocks remain active. Overcurrent and resistor flags must match board wiring.

## Test Signals

Probe on boards using internal/external resistors, verify interrupt delivery, run register stress with timing-sensitive accesses, test suspend/resume and remote wakeup, and validate overcurrent behavior.
