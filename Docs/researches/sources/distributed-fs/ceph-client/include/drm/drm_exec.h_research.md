# sources/distributed-fs/ceph-client/include/drm/drm_exec.h

Purpose: Declares the DRM execution locking helper used to acquire multiple GEM object reservation locks with wound/wait deadlock avoidance and retry-on-contention control flow.

Important APIs, types, and functions: Defines flags `DRM_EXEC_INTERRUPTIBLE_WAIT` and `DRM_EXEC_IGNORE_DUPLICATES`, `struct drm_exec`, object iteration macros, `drm_exec_until_all_locked()`, `drm_exec_retry_on_contention()`, `drm_exec_is_contended()`, and APIs `drm_exec_init()`, `drm_exec_fini()`, `drm_exec_cleanup()`, `drm_exec_lock_obj()`, `drm_exec_unlock_obj()`, `drm_exec_prepare_obj()`, and `drm_exec_prepare_array()`. State includes a `ww_acquire_ctx`, locked-object array, contended/prelocked objects, and capacity counts.

Control flow: Callers initialize an exec context and enter `drm_exec_until_all_locked()`, which cleans up at loop entry and sets a local retry label. Inside the loop, callers prepare or lock each GEM object; if contention is recorded, `drm_exec_retry_on_contention()` jumps back, releases locks, and retries with ww-mutex ordering. Once all locks are acquired, the caller submits or validates work, then finalizes and unlocks via cleanup/fini.

State and persistence: State is transient per submission or validation path. It stores references to currently locked GEM objects and ww acquisition state only for the duration of the operation.

Dependencies and integration points: Depends on GEM objects and Linux ww-mutexes. Integrates with command submission, eviction, validation, GPUVM updates, and any path that needs multiple reservation locks while handling duplicate objects and interruptible waits.

Risks and test signals: Risks include using the retry macro outside its loop body, unsigned reverse-iteration surprises, leaked locks on error paths, duplicate object handling mistakes, sleeping behavior when interruptible waits are requested, and failure to reserve fence slots before submission. Test locking arrays with duplicates, contention against another thread, signal interruption, reverse unlock order, fence reservation counts, and error unwind paths.
