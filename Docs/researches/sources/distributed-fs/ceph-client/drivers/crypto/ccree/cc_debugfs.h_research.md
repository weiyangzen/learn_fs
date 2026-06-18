<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h

Purpose: provides the debugfs interface contract with compile-time stubs when debugfs is disabled.

Important APIs, types, and functions: declares `cc_debugfs_global_init()`, `cc_debugfs_global_fini()`, `cc_debugfs_init()`, and `cc_debugfs_fini()` under `CONFIG_DEBUG_FS`. The non-debugfs path provides no-op inline functions and a successful `cc_debugfs_init()` stub.

Control flow: driver module init/remove can call these functions unconditionally. If debugfs is disabled, calls compile to no-ops and device probe continues normally.

State and persistence behavior: no state in this header. Runtime state is owned by `cc_debugfs.c` only when debugfs is compiled in.

Dependencies and integration points: relies on forward visibility of `struct cc_drvdata` from includers, and is included by `cc_driver.c`. It isolates the platform driver from `#ifdef CONFIG_DEBUG_FS` call-site clutter.

Risks: stubs make debugfs absence silent, so tests that depend on debugfs must check kernel config. Header guard comment names `__CC_SYSFS_H__`, which is cosmetic but can confuse maintainers.

Test signals: build with `CONFIG_DEBUG_FS=y` and `n`, verify probe succeeds in both cases, and confirm debugfs cleanup paths are not referenced when compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h -->
