# sources/cloud-native/containers-storage/drivers/graphtest/graphtest_unix.go

## Purpose
`graphtest_unix.go` is the shared graphdriver behavioral test suite for Unix-like platforms. It standardizes setup, cleanup, and tests that concrete drivers call from their own test files.

## Important APIs, Types, And Functions
`Driver` wraps `graphdriver.Driver` with root/runRoot/refCount. Setup helpers include `newGraphDriver`, `newDriver`, `GetDriverNoCleanup`, `GetDriver`, `ReconfigureDriver`, and `PutDriver`. Contract tests include create-empty/base/snapshot/template, deep layer read, diff/apply, changes, quota, echo, and list layers.

## Control Flow
Driver setup creates temporary roots and skips unsupported/prerequisite/permission failures. Tests create layers, mutate files, call driver methods, compare archive changes, validate file metadata, and register cleanup removals. `GetDriverNoCleanup` allows suites to reuse an expensive driver across multiple tests until `PutDriver` decrements the refcount to zero.

## State And Persistence
State lives in temporary root and runRoot directories. A package-global `drv` caches a shared driver and its refcount. Layer contents and driver metadata are real filesystem artifacts removed during cleanup.

## Dependencies And Integration Points
Concrete driver tests for AUFS, Btrfs, overlay, and others import these helpers. Dependencies include `graphdriver`, `archive`, `stringid`, `go-units`, `testify`, and Unix syscalls.

## Risks
The global driver makes test ordering/refcount discipline important. Tests are integration-heavy and can skip due to environment. Quota tests expect write failures with `EDQUOT`, which depends on backend quota enforcement.

## Test Signals
This file is the main cross-driver signal for graphdriver correctness: create/snapshot inheritance, template identity, diff/apply round trips, deletion whiteouts, metadata preservation, deep layer visibility, quota behavior, echo edge cases, and exact layer listing.
