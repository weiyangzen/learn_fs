# sources/distributed-fs/ceph-client/include/linux/mfd/rz-mtu3.h

## Purpose

This 191-line header defines shared register offsets, bitfields, channel state, and access helpers for Renesas RZ MTU3 multi-function timer channels.

## Important APIs, Types, and Functions

It contains shared/channel-specific register offsets for 8-, 16-, and 32-bit accesses, mode/control bitfield macros, `enum rz_mtu3_channels`, `struct rz_mtu3_channel`, `struct rz_mtu3`, inline `rz_mtu3_request_channel()`/`rz_mtu3_release_channel()`, enable/disable/status prototypes, and read/write/update helpers for channel and shared registers.

## Control Flow

The inline request path locks the channel mutex, checks `is_busy`, marks the channel busy, and returns success or false. Release clears the flag under the same lock. Runtime child drivers then enable the channel and perform typed register accesses through the parent implementation.

## State and Persistence Behavior

`is_busy` is driver-owned allocation state; `struct rz_mtu3` owns the module clock and channel array. Timer count, compare, output, mode, and shared start registers persist in hardware while the module is powered.

## Dependencies and Integration Points

It includes clock, device, and mutex headers. Integration points include PWM, counter, clockevent, and timer child drivers that share MTU3 channels without colliding.

## Risks and Edge Cases

Channel 5 has different register layout and must use MTU5-specific offsets. Callers must release channels on failure paths. Mixed-width register access must match the hardware register size.

## Test Signals

Build coverage for MTU3 children, request/release concurrency tests, register offset tests for channel 5 versus others, and hardware PWM/counter enable-disable smoke tests.
