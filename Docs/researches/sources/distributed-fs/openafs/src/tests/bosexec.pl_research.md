<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosexec.pl -->
# sources/distributed-fs/openafs/src/tests/bosexec.pl

## Purpose
Tests remote BOS execution of an installed script by checking for its side effect.

## Important APIs, Types, And Functions
Uses `AFS_bos_exec`, `OpenAFS::ConfigUtils`, `OpenAFS::Dirpath`, and `OpenAFS::OS`.

## Control Flow
Initializes AFStools, calls `bos exec` for `$openafsdirpath->{'afssrvbindir'}/foo.sh`, verifies `/tmp/garbage` was created, deletes it, and exits `0`.

## State And Persistence
Runs server-side command and temporarily creates `/tmp/garbage`.

## Dependencies And Integration Points
Requires `bosinstall.pl` to install `foo.sh` first and expects Dirpath global availability.

## Risks And Test Signals
The script references `$openafsdirpath` without qualification/import visible in the file, which may be a bug unless imported by modules. Success is the `/tmp/garbage` side effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosexec.pl -->
