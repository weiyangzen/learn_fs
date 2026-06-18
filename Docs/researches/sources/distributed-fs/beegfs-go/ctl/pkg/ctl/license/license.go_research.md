# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/license/license.go

## Purpose
Fetches, interprets, and validates BeeGFS license state, including expiry warnings and capacity-limit violations. It provides reusable health-check logic distinct from CLI-specific license printing.

## Important APIs, Types, And Functions
Exports constants for license feature prefixes, `CheckResult`, `Check`, `GetLicense`, `TotalStorageCapacity`, `CheckIfOverStorageCapacityLimit`, and `GetTimeToExpiration`. `CheckResult.IsHealthy` is the main health predicate.

## Control Flow
`Check` calls `GetLicense`, returns an error result on fetch failure, returns invalid message for non-valid verify result, computes warning-window expiry text, then scans DNS names for `io.beegfs.capacity.*` constraints and validates them against total storage target capacity. Temporary licenses use a 14-day warning window; other licenses use 90 days.

## State And Persistence
No local persistence. It reads license data from management and target capacity from management-derived target information. It intentionally ignores malformed capacity limits and target-fetch failures after debug logging, so license health is not blocked by those secondary checks.

## Dependencies And Integration Points
Uses `config.ManagementClient`, protobuf management/license messages, `ctl/pkg/ctl/target.GetTargets`, BeeGFS entity types, `unitconv` for human-readable capacity, `strfmt.ExpirationString`, and zap debug logging.

## Risks And Edge Cases
`Check` only records the last capacity violation encountered because `ViolationsMsg` is overwritten in the DNS-name loop. Capacity totals require `TotalSpaceBytes` for every storage target and error if any is nil, but that error is ignored by capacity-limit checking. `GetTimeToExpiration` subtracts 12 hours from the certificate validity time, so callers must understand this grace-period adjustment. Floating conversion for huge byte values may lose precision in human-readable output.

## Test Signals
No direct tests. Valuable coverage would include valid/invalid license responses, temporary versus permanent expiry windows, unlimited/malformed/numeric capacity limits, nil target capacity, and multiple DNS capacity entries.
