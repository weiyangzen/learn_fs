# sources/distributed-fs/coda/coda-src/venus/venus.cc

## Purpose
This file is the Venus process entry point and startup orchestrator. It parses command-line/configuration values, sets defaults, daemonizes, initializes every major subsystem in a strict order, mounts the Coda filesystem when enabled, runs the main select/daemon dispatch loop, and performs orderly shutdown.

## Important APIs, Types, and Functions
Important exported globals include root fid/node id, cache/log/spool/config paths, cache sizes, primary user, mariner settings, ASR state, codatunnel flags, and zone limits. `MUX_add_callback()` lets modules add/remove fd callbacks to the main select loop; `_MUX_FD_SET()` and `_MUX_Dispatch()` service them. `ParseSizeWithUnits()`, `power_of_2()`, and `ParseCacheChunkBlockSize()` parse size options. `main()` performs process startup. `ParseCmdline()`, `DefaultCmdlineParms()`, `CalculateCacheFiles()`, `CdToCacheDir()`, `CheckInitFile()`, `UnsetInitFile()`, and `SetRlimits()` handle configuration and environment setup.

## Control Flow
Startup parses command line first, then `venus.conf`, daemonizes if configured, writes pid/control paths, moves into the cache directory, handles INIT metadata wiping, raises data rlimits, tests the kernel device, optionally starts codatunnel, then initializes LWP/vproc, logging, daemon registry, stats, signals, directory storage, recovery, communication, users, VSGs, realms, volumes, FS objects, HDB, mariner, workers, and callbacks. The main loop builds an fd set from registered callbacks, waits through `VprocSelect()` with daemon expiry, dispatches ready callbacks, checks `TerminateVenus`, and fires ready daemons.

## State and Persistence Behavior
Most globals are process configuration. Persistent behavior is driven by `InitMetaData`, `InitNewInstance`, RVM path/size options, cache directory `INIT` file handling, and recovery initialization. `CdToCacheDir()` creates `CACHEDIR.TAG`; `CheckInitFile()` translates the presence of `INIT` into metadata reinitialization; `UnsetInitFile()` removes the marker after successful startup. Shutdown flushes/terminates recovery and unmounts the VFS.

## Dependencies and Integration Points
It integrates every Venus subsystem: recovery, communication, users, VSGDB, RealmDB, volume DB, FSDB, HDB, mariner, kernel worker, callbacks, signal handlers, daemonizer, codatunnel, codaconf, and optional Cygwin IPC. Initialization order is explicitly documented as important, especially `RecovInit < VSGInit < VolInit < FSOInit < HDB_Init`.

## Risks and Test Signals
Risks include initialization-order regressions, config/command-line precedence bugs, size parsing overflow/truncation, invalid cache chunk block sizes, fd-callback removal callbacks, daemonization synchronization, and shutdown paths called both from main loop and signal handlers. Tests should cover config defaults, command-line overrides, INIT file semantics, no-codafs/nofork modes, codatunnel toggles, callback add/update/remove, and startup failure for invalid cache/RVM sizes.
