# sources/cloud-native/moby/daemon/container_windows.go

## Purpose
Provides the Windows stub for AppArmor configuration.

## Important APIs, Types, And Functions
- `saveAppArmorConfig(container *container.Container) error` always returns nil.

## Control Flow
No logic is performed because AppArmor does not apply to Windows containers.

## State And Persistence
Does not mutate container state.

## Dependencies And Integration Points
Keeps the daemon build portable by satisfying the same method used by non-Windows container setup paths.

## Risks And Edge Cases
Shared code must not infer AppArmor state on Windows. This stub should remain intentionally empty unless Windows gains an equivalent security-profile abstraction with a different name.

## Test Signals
No direct tests are needed beyond Windows build coverage.
