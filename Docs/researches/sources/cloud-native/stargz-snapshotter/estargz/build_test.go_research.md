# sources/cloud-native/stargz-snapshotter/estargz/build_test.go

Purpose: Tests eStargz build-time tar reordering and the count read seeker helper.

Important APIs tested: `Build`, `WithPrioritizedFiles`, `WithAllowPrioritizeNotFound`, `sortEntries` behavior through decompressed output, landmark handling, and `newCountReadSeeker`.

Control flow: `TestSort` defines many tar layouts and prioritized logs, runs each case across source compression modes plus log/tar path prefixes, builds an eStargz, decompresses it with gzip, skips TOC entries, and compares tar headers and payloads against expected order. It also verifies allowed missing file reporting. `TestCountReader` performs read and seek operation sequences and checks the tracked current position.

State and persistence: Uses in-memory tar construction and streamed build outputs. No durable state.

Dependencies and integration: Uses helper functions from estargz test utilities, gzip, tar, reflect, and bytes.

Risks covered: No-log no-prefetch landmark insertion, prioritized landmark insertion, directory-parent movement, hardlink target movement, symlink/device/fifo handling, long names, existing landmark removal, missing prioritized files, duplicate entries, and root-relative/absolute names.

Test signals: Strong coverage for ordering semantics. It does not directly validate parallel partition offset recombination, diffID/uncompressed size finalization, or gzip helper execution.
