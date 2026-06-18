<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.cc -->
# sources/distributed-fs/lizardfs/src/common/metadata.cc

## Purpose
Implements metadata/changelog filename constants, metadata version validation, changelog version scanning, and one-time old changelog migration. The source was read completely for this report.

## Important APIs, Types, And Functions
`metadataGetVersion`, `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, `changelogsMigrateFrom_1_6_29`, filename constants, and `gMetadataLockfile` are defined.

## Control Flow
Metadata version parsing opens the file, validates known signatures, extracts version, then verifies the expected EOF marker. Changelog first-version reads a prefix and parses digits before colon. Last-version mmaps the file, requires final LF, walks backward to the previous line, and parses digits before colon. Migration renames `<name>.<i>.mfs` to `<name>.mfs[.<i>]` when safe.

## State And Persistence Behavior
Persistent state is metadata, changelog, sessions files, and the global metadata lockfile pointer. Functions perform filesystem reads/renames but do not modify metadata contents.

## Dependencies And Integration Points
Depends on POSIX file/mmap APIs, `cwrap`, `datapack`, `mfserr`, `slogger`, lockfile, and exception types.

## Risks And Edge Cases
Missing `fstat` error check in last-log path, mmap lifetime on exceptions before `munmap`, and strict newline/colon parsing are notable risks. Migration logs conflicts but leaves manual cleanup.

## Test Signals
Needs filesystem tests with old/new signatures, truncated EOF markers, empty/truncated/malformed changelogs, mmap failures, and migration collision cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.cc -->
