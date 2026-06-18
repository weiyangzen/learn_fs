# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.h

## Purpose
Declares the real-time changelog dispatcher state and lifecycle/enqueue functions.

## APIs, Types, and Functions
Defines `changelog_rt_t` with a `gf_lock_t`. Declares `changelog_rt_init()`, `changelog_rt_fini()`, and `changelog_rt_enqueue()`.

## Control Flow, State, and Persistence
No direct control flow in the header. It describes a dispatcher mode whose only private state is a lock, with persistence handled by the shared change handler.

## Dependencies and Integration
Includes Gluster locking/timer headers and `changelog-helpers.h`. Used by bootstrap code and `changelog-rt.c`.

## Risks and Test Signals
Risks include the “unused as of now” comment drifting from actual use and the minimal state limiting future mode extension. Test signals are compile coverage and mode initialization checks.
