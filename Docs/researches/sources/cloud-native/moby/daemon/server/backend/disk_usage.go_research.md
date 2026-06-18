# sources/cloud-native/moby/daemon/server/backend/disk_usage.go

## Purpose
Defines backend contracts for system disk usage reporting.

## Important APIs, Types, And Functions
`DiskUsageOptions` selects containers, images, volumes, and verbose detail. `DiskUsage` groups image, container, volume, and build cache reports. Type aliases expose API disk usage types for containers, images, and volumes.

## Control Flow
Type definitions only.

## State And Persistence
No state is mutated. Values returned through these structs represent computed daemon storage state.

## Dependencies And Integration Points
Used by `/system/df` handlers and daemon disk usage implementations. Integrates API types from build, container, image, and volume packages.

## Risks And Edge Cases
Verbose options can be expensive in backend implementations. Nil pointers in `DiskUsage` represent omitted categories and must be handled by response writers.

## Test Signals
System disk usage tests and API response tests validate this contract.
