# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.c

Purpose: Implements an Xe validation transaction wrapper around `drm_exec`/`drm_gpuvm_exec_lock` with an rwsem-based validation domain that can retry allocation/locking after OOM by excluding competing validators for exhaustive eviction.

Important APIs/types/functions: Debug-only `xe_validation_assert_exec` validates special exec sentinel pointers. Internal helpers are `xe_validation_lock`, `xe_validation_trylock`, `xe_validation_unlock`, `xe_validation_contention_injected`, and `__xe_validation_should_retry`. Public APIs are `xe_validation_ctx_init`, `xe_validation_exec_lock`, `xe_validation_ctx_fini`, and `xe_validation_should_retry`.

Control flow: Context init stores flags, acquires the validation domain in read or write mode (blocking, interruptible, or trylock), and initializes `drm_exec` if supplied. `xe_validation_exec_lock` wraps `drm_gpuvm_exec_lock`, unlocking and retrying exclusive on qualifying `-ENOMEM`. `xe_validation_should_retry` is intended inside `drm_exec_until_all_locked`; it finalizes/reinitializes `drm_exec`, upgrades to exclusive locking when needed, clears the return value, and tells the macro loop to retry. Fini finalizes `drm_exec` and releases the domain lock.

State and persistence behavior: `struct xe_validation_device` owns an rwsem. `struct xe_validation_ctx` tracks whether the lock is held and whether it is exclusive, requested exclusive mode, flags copied from caller, exec flags, and `nr` for reinitialization. No persistent allocations are made.

Dependencies and integration points: Depends on DRM exec, GEM, GPUVM exec, Xe assertions, and the validation header. Integrated with BO/VM validation paths that need `drm_exec` locking and TTM exhaustive eviction behavior.

Risks: Retry behavior currently treats some WW contention as `-ENOMEM` due to TTM behavior, with a debug slowpath workaround inspecting drm_exec internals. Incorrect use outside `drm_exec_until_all_locked` can break retry control flow. Exclusive upgrade must release read lock before taking write lock to avoid deadlock. Sentinel exec values require careful debug assertions.

Test signals: KUnit or integration tests covering normal shared validation, exclusive validation, no-block failure, interruptible signal interruption, OOM retry upgrade, `drm_gpuvm_exec_lock` retry, debug sentinel assertions, and `CONFIG_DEBUG_WW_MUTEX_SLOWPATH`.
