<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go

## Purpose
Builds in-memory eStargz blobs from synthetic tar entries for tests.

## Important APIs, Types, And Functions
- `buildEStargzOptions` stores estargz and tar builder options.
- `WithEStargzOptions` and `WithBuildTarOptions` configure build behavior.
- `BuildEStargz(ents, opts...)` returns a section reader and TOC digest.

## Control Flow
Options are applied, `BuildTar` creates a tar stream into a buffer, `estargz.Build` converts it, the resulting stream is copied into memory, and a new `io.SectionReader` plus TOC digest are returned.

## State And Persistence
All data is in memory. No files are written.

## Dependencies And Integration Points
Used by tests needing deterministic eStargz blobs. Depends on local tar test utilities and the estargz builder.

## Risks And Edge Cases
Large fixtures are fully buffered twice. Option errors are ignored by the current loop, so failing option functions would not stop the build.

## Test Signals
Tests should verify readable eStargz output, expected TOC digest shape, and preservation of tar entry metadata/content.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/estargz.go -->
