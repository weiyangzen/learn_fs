# sources/distributed-fs/lizardfs/src/mount/g_io_limiters.cc

## Purpose
This file provides process-wide singleton accessors for the mount's local and global I/O limiters. It centralizes lazy construction of limiter state used by `LizardClient::read()` and `write()`.

## Important APIs, Types, And Functions
`gMountLimiter()` returns the local `ioLimiting::MountLimiter`. `gLocalIoLimiter()` constructs a static real-time clock and `LimiterProxy` over the local mount limiter. `gGlobalIoLimiter()` constructs a static `MasterLimiter`, real-time clock, and `LimiterProxy` for master-controlled global limits.

## Control Flow
Each accessor uses function-local statics, so initialization occurs on first call. `LizardClient::fs_init()` forces initialization for global and local limiters, and read/write paths later call the proxies to wait for byte grants.

## State And Persistence
The singletons hold in-memory limiter configuration, clocks, groups, and registered master packet handlers. They persist for the lifetime of the mount process.

## Dependencies And Integration Points
It depends on `common/io_limiting.h` and `mount/global_io_limiter.h`. It integrates with `LizardClient::fs_init()`, local I/O limits loaded from a config file, global I/O limits delivered by the master, and read/write enforcement.

## Risks And Test Signals
Risks include static initialization/lifetime order and packet-handler lifetime for `MasterLimiter`. Test signals come from `global_io_limiter_unittest.cc`, plus mount startup tests with and without an I/O limits config file.
