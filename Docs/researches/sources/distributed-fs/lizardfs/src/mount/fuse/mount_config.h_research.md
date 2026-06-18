# sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.h

## Purpose
This header defines the mount option model used by `mfsmount`, default FUSE mount options, option key ids, global parser symbols, and config/parser function declarations.

## Important APIs, Types, And Functions
`mfsopts_` contains every LizardFS mount option: master host/port/bind/subfolder/passwords, resource limits, debug/meta/delayed init, ACL and cache settings, write-cache settings, chunkserver timeouts, I/O limit config, symlink cache, bandwidth overuse, file locks, and FUSE 3 non-empty mounts. Its constructor seeds defaults from `LizardClient::FsInitParams`. The header also exposes `gMountOptions`, `gCustomCfg`, `gDefaultMountpoint`, `gMfsOptsStage1`, `gMfsOptsStage2`, `usage()`, config parsing, and stage parser callbacks.

## Control Flow
No executable control flow exists here, but construction of the global `gMountOptions` applies all default values before command-line parsing. Compile-time branches determine whether memory locking, file locks, and non-empty mounts exist.

## State And Persistence
The structure owns raw C strings allocated by libfuse parsing or `strdup()`, while numeric and boolean fields carry final mount configuration into `main.cc` and `LizardClient::FsInitParams`. There is no persistence beyond process memory.

## Dependencies And Integration Points
It integrates libfuse, resource-limit headers, platform memory-lock support, protocol defaults, and `LizardClient` defaults. `main.cc` translates this struct into initialization parameters and frees string fields on exit.

## Risks And Test Signals
Raw pointer ownership is the main risk; every added string field needs parsing and cleanup handling. Defaults must stay synchronized with `FsInitParams`. Test signals are compile coverage under different platform/FUSE macros and option parsing tests that assert default values, overrides, and cleanup paths.
