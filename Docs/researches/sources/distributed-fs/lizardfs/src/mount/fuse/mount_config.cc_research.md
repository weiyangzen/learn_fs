# sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.cc

## Purpose
This file defines global mount option storage, the libfuse option tables, help text, config-file parsing, and custom option callbacks used by the mount entrypoint.

## Important APIs, Types, And Functions
`gMountOptions` is the global `mfsopts_` instance consumed by `main.cc`. `gMfsOptsStage1` recognizes only config-file options so config files can be loaded before normal parsing. `gMfsOptsStage2` maps `-o` options and short/long aliases into `mfsopts_` fields or keys. `usage()` prints LizardFS-specific options and libfuse help. `mfs_opt_parse_cfg_file()` reads a config file line by line, ignoring `#`/`;` comments, trimming whitespace, treating absolute paths as default mountpoints, and converting bare options into `-o` pairs. `mfs_opt_proc_stage1()` opens explicit config files. `mfs_opt_proc_stage2()` handles short options, legacy help/version behavior for FUSE 2, and option discarding.

## Control Flow
The parser is intentionally two-stage. Stage 1 loads config-file contents into a default argument vector. Stage 2 first parses that vector into `gMountOptions`, then parses original command-line arguments so explicit CLI options override config defaults. Key callbacks update heap-owned string fields by freeing old values and `strdup()`ing new ones.

## State And Persistence
The file stores global option state, `gCustomCfg`, and `gDefaultMountpoint`. It persists no external data; it only reads config files and allocates option strings that `main.cc` later frees.

## Dependencies And Integration Points
It depends on libfuse option parsing, `mount_config.h`, `LizardClient::FsInitParams` defaults, sugid clear mode string helpers, and compile-time FUSE/platform options. It is the source of truth for CLI/config option names accepted by `mfsmount`.

## Risks And Test Signals
Risks include manual string lifetime, `abort()` on non-optional config open failure, a 1000-byte fixed config line buffer, and compatibility differences in FUSE 2 help/version handling. Test signals include config precedence, default mountpoint parsing, short option parsing, help/version output, `--nonempty` gating, and every `MFS_OPT` field mapping.
