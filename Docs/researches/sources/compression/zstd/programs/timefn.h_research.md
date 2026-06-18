# sources/compression/zstd/programs/timefn.h

## Purpose

This header declares zstd's precise-time abstraction used by CLI progress display, benchmarks, and trace logging.

## Important APIs, Types, and Functions

`PTime` is a 64-bit nanosecond counter type using `uint64_t` when available or `unsigned long long` otherwise. `UTIL_time_t` wraps a `PTime` and has `UTIL_TIME_INITIALIZER`. Declared functions obtain current time, wait for a clock tick, report multi-thread measurement support, and compute elapsed nanoseconds or microseconds. `SEC_TO_MICRO` defines one million microseconds per second.

## Control Flow, State, and Persistence

The header exposes an opaque relative-time contract: absolute `UTIL_time_t` values are not meaningful, only differences between two values are.

## Dependencies and Integration Points

It conditionally includes `<stdint.h>` or `<inttypes.h>` and is used by `timefn.c`, `fileio_common.h`, benchmark code, and tracing.

## Risks and Test Signals

Consumers must not persist or compare absolute timestamps across processes. Tests should compile under C89/C99/C++ modes, verify initializer use, and confirm elapsed-time helpers match expected units.
