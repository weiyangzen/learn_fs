# sources/distributed-fs/lizardfs/src/mount/global_io_limiter.h

## Purpose
This header declares mount-specific limiter types that connect generic I/O limiting to master communication and local mount configuration.

## Important APIs, Types, And Functions
`MasterLimiter : Limiter` sends requests to the master and owns an inner `IolimitsConfigHandler : PacketHandler`. `MountLimiter : Limiter` serves requests from a local `IoLimitsDatabase` and can `loadConfiguration()`. `LimiterProxy` wraps any `Limiter`, classifies pids into groups, and exposes `waitForRead()`/`waitForWrite()` with deadlines.

## Control Flow
The constructor for `LimiterProxy` registers a reconfiguration callback on the wrapped limiter. Reconfiguration and waits are implemented in the `.cc` file.

## State And Persistence
The header defines the shape of in-memory limiter state: config version, handler, database, shared state, mutex, subsystem, group map, enabled flag, and clock reference.

## Dependencies And Integration Points
It includes `common/io_limiting.h` and `mount/mastercomm.h`, and is used by `g_io_limiters.*`, `lizard_client.cc`, and limiter tests.

## Risks And Test Signals
Because `LimiterProxy` stores references to external `Limiter` and `Clock` objects, lifetime must exceed the proxy. Tests in `global_io_limiter_unittest.cc` exercise timing and reconfiguration contracts.
