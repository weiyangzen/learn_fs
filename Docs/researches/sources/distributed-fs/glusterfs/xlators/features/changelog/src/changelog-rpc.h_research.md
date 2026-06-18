# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.h

## Purpose
Declares brick-side changelog RPC listener lifecycle APIs and the public RPC program name.

## APIs, Types, and Functions
Defines `CHANGELOG_RPC_PROGNAME` as `GlusterFS Changelog`. Declares `changelog_init_rpc_listener()`, `changelog_destroy_rpc_listner()`, and `changelog_cleanup_rpc_threads()`.

## Control Flow, State, and Persistence
The header has no state. The declared APIs start the probe listener plus event dispatcher threads, destroy the listener, and clean worker thread/lock resources.

## Dependencies and Integration
Includes `changelog-helpers.h` and `changelog-rpc-common.h`. It is used by main xlator code that manages startup, cleanup, and reconfigure.

## Risks and Test Signals
Risks include spelling compatibility of `listner`, no ownership detail for `rbuf_t`, and cleanup ordering hidden from callers. Test signals are compile coverage and lifecycle tests around init/destroy/reinit.
