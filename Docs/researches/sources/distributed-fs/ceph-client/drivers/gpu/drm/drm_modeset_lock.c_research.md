# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modeset_lock.c

## Purpose
This file implements DRM KMS modeset locking on top of Linux wound/wait mutexes. It provides acquire contexts, deadlock backoff, lock tracking, all-lock helpers, debug diagnostics for improper backoff, and wrappers for single-lock modeset operations.

## Important APIs, Types, and Functions
Core APIs are `drm_modeset_lock_init()`, `drm_modeset_lock()`, `drm_modeset_lock_single_interruptible()`, and `drm_modeset_unlock()`. Acquire-context APIs are `drm_modeset_acquire_init()`, `drm_modeset_acquire_fini()`, `drm_modeset_drop_locks()`, and `drm_modeset_backoff()`. Broad locking helpers are deprecated `drm_modeset_lock_all()` / `drm_modeset_unlock_all()` and preferred `drm_modeset_lock_all_ctx()`. `drm_warn_on_modeset_not_all_locked()` is a debug assertion helper. The file uses a static `DEFINE_WW_CLASS(crtc_ww_class)`.

## Control Flow
Acquire initialization zeroes the context, initializes the WW acquire context, the locked-list head, and interruptible behavior. `drm_modeset_lock()` either behaves like a normal WW mutex when `ctx` is NULL or calls the internal `modeset_lock()` to acquire with the context, track successful locks in `ctx->locked`, tolerate `-EALREADY`, and record a contended lock on `-EDEADLK`. `drm_modeset_backoff()` clears the contended marker, drops all held locks, and takes the contended lock through the slow WW path before the caller retries.

`drm_modeset_lock_all_ctx()` acquires the connection mutex, all CRTC mutexes, all plane mutexes, and all private object locks. Deprecated `drm_modeset_lock_all()` additionally grabs `mode_config.mutex`, creates a global acquire context stored in `mode_config.acquire_ctx`, retries on deadlock, and requires `drm_modeset_unlock_all()` to drop and free that context. Debug-mode stack depot support records where a contended lock was encountered and prints if callers keep locking without backoff.

## State and Persistence Behavior
Each `struct drm_modeset_lock` owns a WW mutex and a list node used only while held by an acquire context. Each acquire context stores the WW context, list of held locks, interruptible/trylock flags, contended lock, and optional debug stack. Deprecated all-lock state persists temporarily in `dev->mode_config.acquire_ctx`. There is no hardware state; this is synchronization state guarding KMS object changes.

## Dependencies and Integration Points
The file depends on WW mutexes, stack depot/stack trace when debug config is enabled, DRM CRTC/plane/private object iteration, and mode_config locking. It is used by atomic commits, property ioctls, legacy KMS paths, connector probing, and helper macros such as `DRM_MODESET_LOCK_ALL_BEGIN()` / `END()`.

## Risks
Callers must handle `-EDEADLK` by invoking `drm_modeset_backoff()` before taking further locks; failing to do so risks deadlock and triggers debug warnings. Deprecated global all-lock helpers are brittle because the acquire context is stored globally and cannot be safely nested. Unlocking a lock not tracked in a context still calls `list_del_init()`, so initialization of the list head is mandatory. Mixing `mode_config.mutex` with WW locks requires consistent ordering outside this file. Interruptible contexts can return `-ERESTARTSYS` from slow paths.

## Test Signals
Signals include lockdep and WW mutex tests for random lock ordering, `-EDEADLK` retry paths through `drm_modeset_backoff()`, `-EALREADY` lock reentry tolerance with a context, interruptible single-lock interruption, all-lock acquisition covering connection, CRTC, plane, and private object locks, deprecated all-lock pairing without leaked `acquire_ctx`, and debug stack output when a caller ignores the backoff protocol.
