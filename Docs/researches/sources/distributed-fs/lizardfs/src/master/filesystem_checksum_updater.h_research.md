# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.h

## Purpose
`filesystem_checksum_updater.h` defines the RAII helper that periodically emits metadata checksum changelog entries after filesystem mutations.

## Important APIs and control flow
In normal builds, `ChecksumUpdater(uint32_t ts)` captures the operation timestamp. Its destructor checks whether `gMetadata->metaversion > lastEntry_ + period_`; if so, `writeToChangelog(ts_)` records the current metadata version, calculates `fs_checksum(ChecksumMode::kGetCurrent)`, converts the LizardFS version to a string, and writes a `CHECKSUM(version):value` changelog entry. Entries are emitted only when the process is master and no background checksum recalculation is in progress. `setPeriod` configures the version interval. In `METARESTORE`, `ChecksumUpdater` is an empty stub.

## State and persistence behavior
The static `period_` throttles checksum entries and `lastEntry_` stores the metadata version of the last emitted entry. Checksum entries become part of changelog persistence and are later verified by `fs_apply_checksum`, unless checksum verification is disabled.

## Dependencies and integration points
This header pulls in version formatting, checksum APIs, metadata globals, background updater state, filesystem operations for `fs_changelog`, and personality checks. It is used broadly at the start of mutating operations so the destructor runs after the mutation body.

## Risks and test signals
RAII means early returns still run the destructor, which is desired but requires care because failed operations may not have advanced `metaversion`. Tests should verify no checksum changelog is written while recalculation is active, no entry is written before the interval threshold, entries are master-only, and metarestore builds do not reference master-only symbols.
