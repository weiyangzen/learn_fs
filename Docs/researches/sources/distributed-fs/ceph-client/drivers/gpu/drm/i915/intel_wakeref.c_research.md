# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.c

Purpose: Implements a higher-level wakeref object that wraps runtime PM with first-user/last-user callbacks, async or delayed release, idle waiting, automatic autosuspend extension, and debug ref printing.

Important APIs/functions: `__intel_wakeref_get_first()`, `__intel_wakeref_put_last()`, `__intel_wakeref_init()`, `intel_wakeref_wait_for_idle()`, `intel_wakeref_auto_init()`, `intel_wakeref_auto()`, `intel_wakeref_auto_fini()`, and `intel_ref_tracker_show()`.

Control flow: First acquisition takes an i915 runtime PM wakeref, locks the wakeref mutex, stores the runtime cookie, calls `ops->get()`, and increments the active count. Last put either schedules delayed work when async/contended or calls `ops->put()` under the mutex; only a successful put releases the stored runtime PM wakeref. Delayed work rechecks the count before final put. `intel_wakeref_auto()` extends an existing RPM wakeref using a timer and refcount balancing.

State/persistence: `struct intel_wakeref` holds atomic count, mutex, stored RPM wakeref cookie, callbacks, delayed work, and optional debug tracker. `struct intel_wakeref_auto` holds timer, wakeref cookie, spinlock, refcount, and i915 pointer. Timer/delayed-work state persists until idle/fini.

Dependencies/integration: Depends on `intel_runtime_pm`, i915 workqueues, ref trackers, wait-bit helpers, and callback users such as GT/display subsystems that need park/unpark semantics.

Risks: Callback failure intentionally retains runtime PM until a later retry; callback implementations must reschedule release on deferral. Async put paths must not race with new gets. `intel_wakeref_auto()` assumes the caller already holds an RPM wakelock and only extends an active wakeref. Debug `BUG_ON` behavior differs between debug and normal builds.

Test signals: `intel_wakeref_wait_for_idle()` provides synchronization for tests and teardown. Ref tracker dumps report leaks. Runtime PM cleanup warnings can reveal leaked auto wakerefs.
