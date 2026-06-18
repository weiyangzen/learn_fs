# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_atomic.h

## Purpose
This header declares the atomic-context phase abstraction used by i915 selftests.

## Important APIs, Types, And Functions
It defines `struct igt_atomic_section` with a phase name and begin/end callbacks, and declares `extern const struct igt_atomic_section igt_atomic_phases[]`.

## Control Flow
Consumers include this header, iterate the exported table, and wrap test bodies with the callback pair for each phase.

## State And Persistence
The header stores no state. It exposes constant metadata and function pointers defined in `igt_atomic.c`.

## Dependencies And Integration Points
It has no heavy includes, making it easy to use in low-level selftest files. It integrates with the phase table implementation in `igt_atomic.c`.

## Risks
The abstraction does not enforce callback pairing; caller discipline is required.

## Test Signals
Signals are indirect through tests that iterate the phases and report phase-specific failures by `name`.
