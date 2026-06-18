# sources/distributed-fs/coda/coda-src/vtools/cfs.cc

## Purpose

`cfs.cc` implements the primary Coda client administration command, `cfs`. It is a table-driven CLI that dispatches subcommands to Venus `pioctl` operations for cache management, volume state inspection, ACL changes, mount point handling, disconnected operation controls, reintegration, local-repair actions, and version-vector conflict manipulation.

## Important APIs, Types, and Functions

The central API is `struct command cmdarray[]`, whose entries bind command names, abbreviations, handler functions, usage text, help text, and optional danger prompts. `main()` uses `findslot()` and invokes the selected `PFV3` handler. Shared helpers include `simple_pioctl()`, `repair_pioctl()`, `pioctl_GetFid()`, `pioctl_SetVV()`, `parseHost()`, `getlongest()`, `dirincoda()`, ACL helpers `parseacl()`, `fillrights()`, `getrights()`, and closure helpers `doclosure()`, `findclosures()`, and `validateclosurespec()`. The command handlers cover `_VIOCCKSERV`, `_VIOC_CHECKPOINTML`, `_VIOC_CLEARPRIORITIES`, `_VIOC_REDIR`, `_VIOC_DISCONNECT`, `_VIOC_RECONNECT`, `_VIOC_FLUSHCACHE`, `_VIOCFLUSH`, `_VIOC_FLUSHVOLUME`, repair pioctls, ASR pioctls, fid/path lookup, mount pioctls, ACL get/set, volume status get/set, CML purge/sync/write-disconnect settings, lookaside cache management, and HDB/local-repair repair commands.

## Control Flow

Execution is linear: parse a subcommand, optionally ask the user to confirm dangerous operations through `brave()`, then run the handler. Most handlers validate argument count, populate `struct ViceIoctl`, call `pioctl()`, and print either structured output or `perror()` diagnostics. Multi-object commands loop over paths or fids and continue after per-item failures. `ListVolume()` decodes Venus' packed volume-status buffer in field order. `ListCache()` asks Venus to write results to a temporary file, then copies and unlinks that file. Closure replay/examination parses closure filenames, validates the target volume root, changes directory there, then shells out to `tar tvf` or `tar xvf`.

## State and Persistence Behavior

The program itself keeps only process-local buffers, mostly the global `piobuf`. Persistent effects are delegated to Venus or the filesystem: cache flushes, disconnection state, CML checkpoint/purge/reintegration, volume quota, ACLs, mount points, repair exposure, version-vector flags, local record preservation/discard, lookaside database state, and zone limits. `ListCache()` and local-repair listing create transient Venus output files and delete them after copying. Closure replay extracts tar content into the selected Coda volume root and may delete the closure with `-r`.

## Dependencies and Integration Points

The file depends on Coda headers and ABI contracts from `venusioctl.h`, `vice.h`, `prs.h`, `codaconf.h`, `inconsist.h`, and platform networking/filesystem headers. It is tightly coupled to Venus `pioctl` opcodes and output buffer layouts, Coda fid/version-vector structures, Coda ACL bit masks, `/usr/coda/spool` closure naming, `venus.conf` `checkpointdir`, and build-time `SYSTYPE`/`CPUTYPE` definitions.

## Risks

Several handlers mutate high-risk state and are guarded only by an interactive prompt or usage text. Fixed-size `sprintf()`, `strcpy()`, and global buffer packing can overflow if Venus or user inputs exceed expected sizes. `dirincoda()` changes process cwd and does not restore it on all paths. Closure replay builds shell commands with filenames, exposing command-injection risk for hostile closure names. ACL parsing allocates entries without cleanup, acceptable for short CLI lifetime but fragile in libraries. Some packed-buffer decoders assume exact Venus layout and integer sizes. `GetPFid()` and `GetPath()` parse fids with `%x` into Coda fields and append realm strings into `piobuf` without length checks. `ListCache()` opens output with `O_EXCL`, so repeated paths fail instead of replacing. Several comments mark commands as untested or dubious.

## Test Signals

Useful tests include command-table abbreviation dispatch, usage errors, confirmation bypass/decline behavior, ACL round-trip parsing and rights encoding, fid string parsing with malformed realms, mocked `pioctl()` input/output packing for each handler, volume-status buffer decoding, mount path edge cases, `lookaside` command construction at buffer limits, closure filename validation, and integration tests against a test Venus for cache, ACL, mount, repair, write-disconnect, and reintegration commands.
