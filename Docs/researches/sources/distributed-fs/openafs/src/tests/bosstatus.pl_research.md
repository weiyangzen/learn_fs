<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstatus.pl -->
# sources/distributed-fs/openafs/src/tests/bosstatus.pl

## Purpose
Verifies initial long-status parsing for the `sleeper` BOS bnode.

## Important APIs, Types, And Functions
Uses `AFS_bos_status`.

## Control Flow
Reads status for `sleeper`, dereferences the returned hash entry, and requires one start and normal-running status.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on `boscreate.pl` having created and started `sleeper`.

## Risks And Test Signals
Status text is exact and English. Exit `0` validates `AFS_bos_status` output parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstatus.pl -->
