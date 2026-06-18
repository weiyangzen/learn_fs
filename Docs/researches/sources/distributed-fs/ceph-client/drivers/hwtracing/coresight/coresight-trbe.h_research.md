# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.h

## Purpose

`coresight-trbe.h` provides TRBE hardware helper routines for feature detection, status decoding, register access, pointer programming, and include dependencies used by the TRBE driver.

## Important APIs, Types, and Functions

Helpers include `is_trbe_available`, `is_trbe_enabled`, `get_trbe_ec`, `get_trbe_bsc`, IRQ/status predicates, flag/programming/alignment readers, write/base/limit pointer accessors, and TRBE register setters. Constants define TRBE exception classes and buffer status codes.

## Control Flow

The C driver calls these helpers while probing CPU capability, clearing status, setting base/write/limit registers, detecting wrap/fatal/spurious events, and enforcing alignment. Setters warn if programming is attempted while TRBE is enabled or with misaligned pointers.

## State and Persistence Behavior

The header has no persistent C state; it directly reads and writes per-CPU system registers. Hardware register contents persist until reset, disable, CPU power events, or explicit driver writes.

## Dependencies and Integration Points

It includes ACPI, CoreSight, IRQ, OF, platform, SMP, Arm PMU/perf, and `coresight-etm-perf.h`, making it the hardware-facing companion to `coresight-trbe.c`. It depends on arm64 system register definitions.

## Risks and Edge Cases

Inline register helpers assume execution on the target CPU. Misuse from the wrong CPU or while enabled can corrupt active capture, guarded only by `WARN_ON`. Alignment fields from hardware must be interpreted correctly because downstream limit calculation depends on them.

## Test Signals

Probe tests should validate feature detection and alignment extraction. Runtime tests should assert warning-free base/write/limit programming, status predicate correctness, IRQ clearing, and behavior when helpers are called with TRBE disabled versus enabled.
