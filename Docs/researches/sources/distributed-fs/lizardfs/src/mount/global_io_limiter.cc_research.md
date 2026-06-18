# sources/distributed-fs/lizardfs/src/mount/global_io_limiter.cc

## Purpose
This file implements local and master-backed I/O limiter plumbing for mount read/write throttling. It adapts generic `ioLimiting` primitives to LizardFS master protocol messages and Linux cgroup classification.

## Important APIs, Types, And Functions
`MasterLimiter` registers a `LIZ_MATOCL_IOLIMITS_CONFIG` packet handler, sends `cltoma::iolimit` requests with the current config version, validates `matocl::iolimit` replies, and returns granted bytes. `IolimitsConfigHandler::handle()` deserializes master config updates and calls `reconfigure_()`. `MountLimiter::request()` delegates to an `IoLimitsDatabase`; `loadConfiguration()` loads local limits and exposes configured groups. `LimiterProxy::waitForRead()` and `waitForWrite()` classify the pid with `getIoLimitGroupIdNoExcept()`, find the configured group or `unclassified`, and wait on the group's token logic until granted or deadline. `LimiterProxy::reconfigure()` atomically removes stale groups, marks removed groups dead, creates new groups, replaces groups when subsystem changes, updates `delta`, and enables/disables limiting.

## Control Flow
Local configuration is loaded at mount initialization, while global configuration arrives asynchronously from master packets. On each read/write, `LizardClient` calls local proxy first, then global proxy. If a group disappears while waiting, `Group::wait()` returns `ENOENT` and the proxy reclassifies/retries.

## State And Persistence
`MasterLimiter` stores `configVersion_` and packet-handler registration. `MountLimiter` stores an `IoLimitsDatabase`. `LimiterProxy` stores a mutex-protected map of group ids to shared `Group` objects, current subsystem, shared limiter state, clock reference, and enabled flag. State is in memory and driven by config files or master packets.

## Dependencies And Integration Points
It depends on protocol serializers/deserializers, `mastercomm` raw send/receive and packet handler registration, `IoLimitsDatabase`, token-bucket/group primitives, `io_limit_group` cgroup parsing, and syslog logging. Its primary integration point is `LizardClient::read()`/`write()`.

## Risks And Test Signals
Risks include stale config-version rejection, blocking waits under reconfiguration, dead group wakeup semantics, Linux-only `/proc` cgroup classification behavior, and returning `EPERM` when no group is usable. `global_io_limiter_unittest.cc` validates deadlines, no-sleep paths, group death, throughput changes, exact timing across deltas, multi-mount aggregate throughput, and bounded master request counts.
