# sources/distributed-fs/lizardfs/src/mount/g_io_limiters.h

## Purpose
This header declares global accessor functions for the mount's local and global I/O limiting infrastructure.

## Important APIs, Types, And Functions
It exposes `gMountLimiter()`, `gLocalIoLimiter()`, and `gGlobalIoLimiter()`, returning `MountLimiter&` or `LimiterProxy&`.

## Control Flow
No control flow is implemented here. Callers use these accessors to lazily obtain the singleton limiters.

## State And Persistence
No state is declared in the header. State is created in `g_io_limiters.cc` by function-local statics.

## Dependencies And Integration Points
It includes common and mount I/O limiting declarations and is consumed by `lizard_client.cc` during initialization and read/write throttling.

## Risks And Test Signals
The main risk is exposing mutable singleton references. Relevant signals are compile coverage and limiter behavior tests in `global_io_limiter_unittest.cc`.
