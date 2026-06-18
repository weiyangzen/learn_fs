# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/clock.c

## Purpose

This file implements the nVHE tracing clock used to convert architectural counter cycles into nanoseconds at EL2.

## Important APIs, Types, And Functions

It defines `trace_clock_data`, helper `__clock_mult_uint128()`, and APIs `trace_clock_update()` and `trace_clock()`.

## Control Flow

`trace_clock_update()` validates multiplier/shift, writes the inactive bank of conversion parameters, computes overflow threshold, and publishes the new bank with release ordering. `trace_clock()` acquire-loads the active bank, subtracts epoch cycles from `CNTVCT`, uses fast 64-bit multiply when safe, falls back to 128-bit multiply on overflow risk, and adds epoch nanoseconds.

## State And Persistence Behavior

State is a double-buffered static clock structure containing two parameter banks and the current bank selector. Host-provided data is treated as untrusted but read locklessly.

## Dependencies And Integration Points

It depends on arch timer counter reads, division helpers, and nVHE tracing control paths that call `__tracing_update_clock()`.

## Risks And Test Signals

Risks are invalid host conversion parameters, torn bank reads, overflow, and non-monotonic timestamps after bad epochs. Test signals include clock update calls, tracing timestamps before/after bank swaps, large cycle deltas triggering 128-bit conversion, and disabled tracing builds via `clock.h`.
