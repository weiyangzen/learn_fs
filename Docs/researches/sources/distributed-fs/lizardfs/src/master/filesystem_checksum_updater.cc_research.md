# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.cc

## Purpose
`filesystem_checksum_updater.cc` provides storage for `ChecksumUpdater` static state in normal master builds.

## Important APIs and state
The implementation defines `ChecksumUpdater::period_` and initializes `ChecksumUpdater::lastEntry_` to zero when `METARESTORE` is not defined. The class itself is declared inline in the header; this file exists so the static variables have exactly one definition.

## Control flow and persistence behavior
Runtime behavior happens through the header-defined RAII destructor: metadata operations create a `ChecksumUpdater`, mutate metadata, and when the object is destroyed it may emit a `CHECKSUM` changelog entry if the metadata version advanced far enough since `lastEntry_`. This `.cc` file participates by holding the period and last-emitted version.

## Dependencies and integration points
It includes `filesystem_checksum_updater.h` and is compiled only for normal master/shadow builds, not metarestore. `period_` is configured in `filesystem.cc` via `ChecksumUpdater::setPeriod`.

## Risks and test signals
The risk here is linkage/configuration rather than algorithmic behavior. Tests should ensure there is one definition in normal builds, none in metarestore builds, `lastEntry_` starts at zero after process start, and changing `METADATA_CHECKSUM_INTERVAL` updates `period_`.
