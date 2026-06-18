
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.h

Purpose: compile-time abstraction for Intel TH debugfs support.

Important APIs/types/functions: declares `intel_th_dbg`, `intel_th_debug_init()`, and `intel_th_debug_done()` when `CONFIG_INTEL_TH_DEBUG` is set; otherwise provides no-op inline versions of the init/done functions.

Control flow: lets core code call debug init/teardown unconditionally without `#ifdef` blocks in the caller.

State and persistence: no state unless debug support is compiled, in which case `debug.c` owns the global dentry.

Dependencies and integration: included by `core.c` and `debug.c`; relies on Kconfig to decide whether the debug implementation exists.

Risks: consumers must not reference `intel_th_dbg` unless the config path declares it. Adding debugfs child creation outside the same config guard would fail to build.

Test signals: build both with and without `CONFIG_INTEL_TH_DEBUG`; ensure callers link and the no-op path produces no unresolved symbol.
