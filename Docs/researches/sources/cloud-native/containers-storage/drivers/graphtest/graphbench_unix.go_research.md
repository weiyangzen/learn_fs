# sources/cloud-native/containers-storage/drivers/graphtest/graphbench_unix.go

## Purpose
`graphbench_unix.go` provides reusable benchmark helpers for graphdriver implementations on Unix-like systems.

## Important APIs, Types, And Functions
Benchmarks include `DriverBenchExists`, `DriverBenchGetEmpty`, `DriverBenchDiffBase`, `DriverBenchDiffN`, `DriverBenchDiffApplyN`, `DriverBenchDeepLayerDiff`, and `DriverBenchDeepLayerRead`.

## Control Flow
Each benchmark obtains a driver, creates base/upper/deep layers, populates files through testutil helpers, resets the timer, and loops on the operation being measured. Some benchmarks stop the timer for setup/validation inside each iteration.

## State And Persistence
Temporary layer state is created under `graphtest` driver roots. Benchmarks read, write, diff, and apply actual layer filesystem content.

## Dependencies And Integration Points
It depends on `graphdriver`, `stringid`, `testing`, and graphtest helpers such as `addManyFiles`, `checkManyFiles`, and `addManyLayers`.

## Risks
`DriverBenchDiffApplyN` must feed the produced diff reader into `ApplyDiff`; missing or incorrect diff wiring would make benchmark validation fail. Results are highly dependent on backing filesystem and driver behavior.

## Test Signals
Benchmarks serve as performance signals for existence checks, mount/get cost, diff cost, diff/apply cost, and deep-layer read/diff behavior.
