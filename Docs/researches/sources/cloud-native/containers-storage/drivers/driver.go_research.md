# sources/cloud-native/containers-storage/drivers/driver.go

## Purpose
`driver.go` defines the graphdriver interfaces, option types, registration and selection logic, errors, and shared helper contracts used by all storage drivers.

## Important APIs, Types, And Functions
Key types include `FsMagic`, `CreateOpts`, `MountOpts`, `ApplyDiffOpts`, `ApplyDiffWithDifferOpts`, `DedupArgs`, `DedupResult`, `InitFunc`, `ProtoDriver`, `DiffDriver`, `LayerIDMapUpdater`, `Driver`, `DriverWithDifferOutput`, `Differ`, `DriverWithDiffer`, `Capabilities`, `AdditionalLayer`, `AdditionalLayerStoreDriver`, `DiffGetterDriver`, `FileGetCloser`, `Checker`, and `Options`. Key functions include `MustRegister`, `Register`, `GetDriver`, `New`, `ScanPriorDrivers`, `isDriverNotSupported`, and `driverPut`.

## Control Flow
Drivers register in package init functions. `New` uses an explicit driver name when provided, otherwise scans prior driver directories, applies priority ordering, refuses ambiguous prior state, then probes priority and registered drivers until one succeeds or all are unsupported. `driverPut` is a defer helper that merges `Put` errors into an existing return error or logs secondary failures.

## State And Persistence
The global `drivers` map is in-memory registration state. Persistent detection is directory-based through `ScanPriorDrivers(config.Root)`. Options carry root/runroot/image store paths, driver priorities, and driver options into initialization.

## Dependencies And Integration Points
Every driver package depends on these contracts. The file integrates with dedup options, tempdir cleanup, archive diffs, directory usage, idtools, digest metadata, tar-split file getters, fileutils, and logrus.

## Risks
Driver selection protects existing storage by erroring when prior driver state exists but no longer initializes; changing this can make images appear missing. Interface changes have broad blast radius. `DriverWithDiffer` and additional layer APIs are experimental but still used by overlay/composefs flows.

## Test Signals
Concrete driver tests and `graphtest` exercise the contracts. There is no direct registration/selection unit test in this subset.
