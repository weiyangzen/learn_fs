<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go

## Purpose
This fallback quota implementation preserves the quota API on non-Linux, non-cgo, or quota-excluded builds.

## Important APIs, Types, And Functions
It defines the same `Quota` struct and a stub `Control`. `NewControl`, `SetQuota`, and `GetQuota` return errors saying quotas are unsupported; `ClearQuota` is a no-op.

## Control Flow
All modifying/query operations fail immediately except cleanup.

## State And Persistence
No quota state is read or written.

## Dependencies And Integration Points
Build tags select this file for unsupported configurations. Overlay initialization uses the error from `NewControl` to decide whether storage options requiring quota should fail.

## Risks And Test Signals
Callers must gate quota-required behavior on `NewControl` success. This file intentionally does not implement `GetDiskUsage`, because quota-aware usage is only compiled into the overlay disk quota file for supported builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota_unsupported.go -->
