# sources/cloud-native/cri-o/internal/config/capabilities/capabilities_unsupported.go

## Purpose
Unsupported-platform capabilities stub.

## Important APIs, Types, and Functions
Defines Capabilities, Default, and Validate with reduced/no-op behavior for unsupported builds.

## Control Flow
Lets callers compile when Linux capability validation is unavailable.

## State and Persistence
No state.

## Dependencies
Build tags select it off Linux or without capabilities support.

## Integration Points
Keeps config package portable.

## Risks and Edge Cases
May accept fewer validations on unsupported platforms.

## Test Signals
Compile tests validate it.
