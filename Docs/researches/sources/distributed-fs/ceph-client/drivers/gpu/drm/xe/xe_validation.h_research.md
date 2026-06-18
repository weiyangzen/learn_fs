# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_validation.h

Purpose: Defines the validation transaction API, special drm_exec sentinels, flags/state structures, retry macro, and scoped cleanup helper for Xe validation.

Important APIs/types/functions: Provides `XE_VALIDATION_UNIMPLEMENTED`, `XE_VALIDATION_UNSUPPORTED`, and `XE_VALIDATION_OPT_OUT` sentinel exec pointers; `xe_validation_lockdep`; optional `xe_validation_assert_exec`; `struct xe_validation_device`; `struct xe_val_flags`; `struct xe_validation_ctx`; function declarations; `xe_validation_retry_on_oom`; `xe_validation_device_init`; and `xe_validation_guard` based on `DEFINE_CLASS`/`scoped_guard`.

Control flow: Callers initialize a validation device rwsem, create a context with flags, enter `drm_exec_until_all_locked` loops, and use `xe_validation_retry_on_oom` or the scoped guard to handle cleanup and retry. Sentinel exec pointers mark call paths that cannot yet provide a real `drm_exec`.

State and persistence behavior: `xe_validation_device` rwsem persists per validation domain. `xe_validation_ctx` persists for one transaction and records lock/exec state required for retry and cleanup.

Dependencies and integration points: Depends on DMA reservation WW locking, Linux rwsem/types, DRM exec/GEM/GPUVM forward declarations, and C cleanup-class macros. Integrated with memory allocation, eviction, VM validation, and tests that opt out of full validation.

Risks: Sentinel values are encoded as `ERR_PTR` with negative constants; they must not be passed to normal `drm_exec` operations. The retry macro uses `goto *__drm_exec_retry_ptr`, so it must be used only in the expected DRM exec macro context. Comments contain typos but the API contract is clear.

Test signals: Compile with and without debug/prove-locking, exercise scoped guard cleanup, sentinel assertion paths, retry macro behavior under OOM, and lockdep validation that transactions can be initialized at sentinel use sites.
