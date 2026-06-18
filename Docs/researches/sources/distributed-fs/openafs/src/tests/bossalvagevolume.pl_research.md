<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl

## Purpose
Smoke-tests salvaging one volume, `unrep`, on partition `a`.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", "a", "unrep", ...)`.

## Control Flow
Initializes AFStools, invokes volume-specific salvage, and exits `0` if no wrapper exception occurs.

## State And Persistence
May modify the `unrep` volume's on-disk metadata and salvage logs.

## Dependencies And Integration Points
Depends on `afs-newcell.pl` creating the `unrep` volume.

## Risks And Test Signals
Exact BOS output around salvage start/completion is parsed. Success confirms the wrapper's partition/volume argument path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagevolume.pl -->
