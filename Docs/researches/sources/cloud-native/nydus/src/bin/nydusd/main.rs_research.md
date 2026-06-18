# sources/cloud-native/nydus/src/bin/nydusd/main.rs

## Purpose
`main.rs` is the `nydusd` daemon entrypoint. It defines all daemon modes and global options, initializes logging/signals/resource limits/dedup, constructs the requested daemon service, starts the optional administration API, runs the daemon controller event loop, and performs shutdown.

## Important APIs, Types, And Functions
Global lazy statics are `DAEMON_CONTROLLER`, `BTI_STRING`, and `BTI`. CLI construction helpers include `append_fs_options`, `append_fuse_options`, feature-gated `append_virtiofs_options`, `append_fscache_options`, singleton options, and block-mode option builders. Runtime helpers are `handle_rlimit_nofile_option`, `process_fs_service`, `process_singleton_arguments`, feature-gated `process_nbd_service` and `process_uffd_service`, `sig_exit`, and `main`.

## Control Flow
`main` parses options, initializes logging, registers SIGINT/SIGTERM handlers, logs build info, applies `rlimit-nofile`, optionally initializes CAS dedup, then dispatches by subcommand. Default and `fuse` paths call `process_fs_service` with FUSE mode. `virtiofs` calls the same helper with non-FUSE mode. `singleton` creates a daemon hosting shared blobcache/fscache services. Feature-gated `nbd` and `uffd` create block daemons. After construction, `main` registers the default filesystem service in `DAEMON_CONTROLLER`, starts `ApiServerController`, runs the controller loop if active, then stops API threads and shuts down the daemon.

## State And Persistence
Daemon state is stored in `DAEMON_CONTROLLER`: selected daemon, default filesystem service, singleton mode, blob-cache manager, and event-loop wakers. Persistent effects include mounted FUSE/virtiofs/block services, fscache/blobcache work directories, NBD/UFFD sockets/devices, optional dedup database usage, API socket files, log files, and resource-limit changes. `process_fs_service` may synthesize localfs JSON config, inject `IMAGE_PULL_AUTH` into registry config, and read prefetch file lists.

## Dependencies And Integration Points
The file integrates Clap, shared `nydus` logging/build-info/signal helpers, `nydus_service` daemon factories, `ConfigV2`, `CasMgr`, feature-gated virtiofs/NBD/UFFD modules, and the API server glue. It is the root for runtime modes consumed by external supervisors and by `nydusctl`.

## Risks
Mode-specific option compatibility is spread across Clap definitions and runtime checks. `hybrid-mode` uses `ArgAction::SetFalse`, so presence semantics are easy to misread. Some generated JSON config is built with string formatting/replacement. `process_fs_service` only creates a virtiofs daemon inside a feature gate; non-FUSE mode without the feature would not set one. `rlimit-nofile` depends on platform sysctl/proc values and can fail daemon startup. Signal handlers call into global controller state from a C handler context.

## Test Signals
There are no direct unit tests. Integration coverage should include default FUSE invocation, explicit `fuse`, `singleton`, feature-gated `virtiofs`, `nbd`, and `uffd`, API socket lifecycle, signal shutdown, `IMAGE_PULL_AUTH` config injection, prefetch-file parsing, localfs synthesized config, rlimit handling, log rotation option parsing, and dedup database initialization.
