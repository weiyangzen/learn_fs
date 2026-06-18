# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_exec_test.c

Purpose: provides KUnit coverage for the DRM exec helper's object locking, duplicate handling, prepare helpers, and loop lifecycle. The tests target the `drm_exec` API used by drivers to lock multiple GEM reservation objects under wound/wait retry rules.

Important APIs/types/functions: `struct drm_exec_priv` stores a parent device and DRM device allocated by `drm_exec_test_init()` using DRM KUnit helpers. Tests call `drm_exec_init()`, `drm_exec_fini()`, `drm_exec_until_all_locked`, `drm_exec_lock_obj()`, `drm_exec_unlock_obj()`, `drm_exec_retry_on_contention()`, `drm_exec_prepare_obj()`, and `drm_exec_prepare_array()`. GEM objects are initialized with `drm_gem_private_object_init()` and finalized where needed with `drm_gem_private_object_fini()`.

Control flow: `sanitycheck()` only initializes/finalizes an exec object. `test_lock()` creates one GEM object and locks it inside the `drm_exec_until_all_locked` retry loop. `test_lock_unlock()` locks, unlocks, and relocks the same object within one exec context. `test_duplicates()` initializes with `DRM_EXEC_IGNORE_DUPLICATES`, locks the same object twice, then explicitly unlocks once before finalization. `test_prepare()` uses `drm_exec_prepare_obj()` to prepare one object with a single fence slot. `test_prepare_array()` allocates two GEM objects and prepares them together. `test_multiple_loops()` verifies separate exec loop instances can be initialized and finalized back to back without stale state.

State and persistence: state is limited to KUnit allocations, transient `struct drm_exec`, embedded GEM object reservation state, and object reference/lock state. There is no persistent storage. Some tests use stack-allocated GEM objects, while the array test uses KUnit-allocated heap objects and explicit GEM finalization.

Dependencies and integration points: depends on DRM device/GEM core initialization through `DRIVER_MODESET`, Linux prime-number support indirectly through `drm_exec`, and the reservation locking machinery behind GEM objects. The tests are direct API users and serve as examples of the required retry-loop idiom.

Risks: the tests mostly cover uncontended paths; they do not simulate actual ww-mutex contention, interrupts, or deadlock retries. Stack-allocated GEM objects must be correctly initialized before locking and finalized when object lifetime requires it. `test_duplicates()` depends on duplicate-ignore semantics balancing lock/unlock accounting. Changes to `drm_exec_until_all_locked` macro behavior can affect control-flow assumptions, especially around `ret` assignment and retry labels.

Test signals: KUnit failures show nonzero returns from lock/prepare helpers or loop/finalization problems. Regression signals include duplicate locking returning an error under `DRM_EXEC_IGNORE_DUPLICATES`, prepare-array failure for multiple objects, or state leakage preventing consecutive exec loops.
