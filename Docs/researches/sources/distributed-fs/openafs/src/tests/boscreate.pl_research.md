<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boscreate.pl -->
# sources/distributed-fs/openafs/src/tests/boscreate.pl

## Purpose
Creates and starts a simple BOS bnode named `sleeper` for BOS lifecycle tests.

## Important APIs, Types, And Functions
Uses local file I/O, `chmod`, `AFS_bos_install`, and `AFS_bos_create`.

## Control Flow
Writes an executable `sleeper.sh` that sleeps forever, installs it through BOS, creates a simple bnode with command `/usr/afs/bin/sleeper.sh`, and exits `0`.

## State And Persistence
Creates local `sleeper.sh`, installs it into the server binary directory, and writes a BosConfig entry for the `sleeper` bnode.

## Dependencies And Integration Points
Foundational state for `bosstatus`, `bosstop`, `bosstart`, `bosshutdown`, `bosrestartstopped`, `bosdeleterunning`, and `bosdelete`.

## Risks And Test Signals
Hard-codes `/usr/afs/bin/sleeper.sh`, which may not match Dirpath on all platforms. Success is a running `sleeper` status stanza.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boscreate.pl -->
