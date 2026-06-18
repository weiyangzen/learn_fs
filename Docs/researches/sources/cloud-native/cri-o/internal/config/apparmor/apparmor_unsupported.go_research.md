# sources/cloud-native/cri-o/internal/config/apparmor/apparmor_unsupported.go

## Purpose
Unsupported-platform AppArmor stub.

## Important APIs, Types, and Functions
Defines DefaultProfile, Config, New, LoadProfile and likely no-op/disabled behavior for non-Linux or no_apparmor builds.

## Control Flow
Calls return disabled/no-op behavior so callers can compile without AppArmor.

## State and Persistence
No state beyond Config fields.

## Dependencies
Build tags select this file when Linux AppArmor implementation is unavailable.

## Integration Points
Keeps config package portable.

## Risks and Edge Cases
Feature silently unavailable on unsupported builds.

## Test Signals
Compile-only/unsupported platform tests validate it.
