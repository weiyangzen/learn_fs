# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_reset.h

## Purpose
This header declares reset helpers used by i915 selftests.

## Important APIs, Types, And Functions
It forward-declares `struct intel_gt` and declares `igt_global_reset_lock()`, `igt_global_reset_unlock()`, and `igt_force_reset()`.

## Control Flow
Callers lock around reset-sensitive operations, unlock afterward, or call force reset to provoke recovery.

## State And Persistence
No state in the header; implementation mutates GT reset state.

## Dependencies And Integration Points
The header keeps reset helper consumers decoupled from the full reset implementation headers.

## Risks
The lock API is manual and must be paired.

## Test Signals
The only direct signal is the boolean return from `igt_force_reset()`.
