# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.h

## Purpose
`filesystem_checksum_background_updater.h` declares the background checksum recalculation state machine and its step enum.

## Important APIs and types
`ChecksumRecalculatingStep` enumerates `kNone`, `kNodes`, `kXattrs`, `kChunks`, and `kDone`. The overloaded prefix `operator++` advances the enum and asserts that `kDone` is not incremented. `ChecksumBackgroundUpdater` exposes lifecycle methods (`start`, `end`, `reset`), status accessors (`inProgress`, `getStep`, `getPosition`, `getSpeedLimit`), cursor mutation (`incStep`, `incPosition`), inclusion tests (`isNodeIncluded`, `isXattrIncluded`), and checksum values (`fsNodesChecksum`, `xattrChecksum`).

## Control flow and integration
The header documents that actual scanning is performed outside the class by `fs_background_checksum_recalculation_a_bit()`. The class is a small state holder used by filesystem checksum code, xattr checksum code, periodic chunk checksum logic, and live metadata mutations.

## State and persistence behavior
The class does not persist data directly. Its public checksum fields are transient recalculation aggregates that can replace `gMetadata` checksum fields at the end of a run. The `speedLimit_` value comes from config and controls latency versus convergence time.

## Risks and test signals
Because `operator++` relies on enum ordering, adding a new step requires auditing all switch statements and inclusion checks. Tests should verify step ordering, reset seeds, position reset on `incStep`, and compile coverage for any new enum value in the periodic recalculation switch.
