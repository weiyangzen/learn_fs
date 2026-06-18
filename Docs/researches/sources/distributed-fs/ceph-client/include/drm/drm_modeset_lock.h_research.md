# sources/distributed-fs/ceph-client/include/drm/drm_modeset_lock.h

Purpose: declares DRM modeset locking primitives built on wound/wait mutexes, plus helper macros for acquiring all modeset locks with deadlock backoff.

Important APIs and types: `struct drm_modeset_acquire_ctx` wraps `ww_acquire_ctx`, tracks the contended lock, optional stackdepot debugging, list of held locks, trylock-only mode for panic contexts, and interruptible behavior. `struct drm_modeset_lock` wraps a `ww_mutex` plus list node used while held in an atomic update. APIs initialize/finalize acquire contexts, drop locks, back off after `-EDEADLK`, initialize/finalize individual locks, test/assert lock state, lock/unlock one lock, take one interruptibly, lock/unlock all device modeset locks, warn if not all locked, and lock all with a caller-provided context. `DRM_MODESET_LOCK_ALL_BEGIN/END` wrap retry/backoff boilerplate.

Control flow: callers initialize an acquire context, attempt to lock required modeset resources, and if any lock returns `-EDEADLK`, jump to cleanup/backoff, slow-lock the contended lock, and retry. The all-lock macros also take the legacy mode-config mutex for non-atomic drivers.

State and persistence behavior: held locks are linked into the acquire context until dropped. The contended pointer and debug stack record unresolved deadlock handling. Individual modeset locks persist inside CRTCs, planes, connectors, and mode-config objects.

Dependencies and integration points: uses Linux ww_mutex, stackdepot, lockdep, and DRM device/object declarations. It is foundational for atomic state acquisition, legacy modeset serialization, and helper callbacks that may add more state.

Risks: every `-EDEADLK` must trigger the backoff dance or deadlocks and debug warnings follow. `trylock_only` is for panic paths and cannot be used for normal blocking updates. Non-atomic and atomic drivers differ in whether the mode-config mutex is also taken. `drm_modeset_lock_fini()` warns if the lock is still linked.

Test signals: atomic commits acquiring multiple object locks, forced deadlock retry paths, interruptible lock acquisition, all-lock macros on atomic and non-atomic drivers, lockdep assertions, panic trylock users, and cleanup with no held lock list entries.
