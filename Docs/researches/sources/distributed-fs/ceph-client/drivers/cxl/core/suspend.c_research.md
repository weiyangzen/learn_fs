# sources/distributed-fs/ceph-client/drivers/cxl/core/suspend.c

Purpose: provides a tiny shared active-CXL-memory counter used by CXL memory drivers and suspend/PM policy code to know whether CXL memory is currently active.

Important APIs and control flow: `cxl_mem_active()` returns whether the atomic counter is nonzero. `cxl_mem_active_inc()` increments the counter and is exported in the CXL namespace. `cxl_mem_active_dec()` decrements the counter and is also exported. There is no init/exit flow beyond static zero initialization of `mem_active`.

State and persistence behavior: all state is a single static `atomic_t mem_active`. It persists for module lifetime and is not tied to an individual device. The file does not guard against underflow; callers must balance increments and decrements.

Dependencies and integration points: depends on Linux atomics and CXL mem headers. It integrates with CXL memory activation paths elsewhere in the driver tree and any suspend logic that checks `cxl_mem_active()`.

Risks and test signals: the primary risk is imbalance, especially on probe/remove or error paths, because a negative atomic value still makes `cxl_mem_active()` return true. Test signals include activation/deactivation balance under region probe failures, remove paths, suspend attempts with active memory, and lockdep/KUnit-style assertions in callers that pair inc/dec operations.
