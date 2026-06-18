<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/selftest.h

Purpose: declares or stubs the Bluetooth selftest entry point according to `CONFIG_BT_SELFTEST` and whether the Bluetooth core is built as a module.

Important APIs/types/functions: when `CONFIG_BT_SELFTEST` is enabled and `CONFIG_BT` is a module, it declares `int bt_selftest(void);`. Otherwise it provides a static inline `bt_selftest` that returns success and has no side effects.

Control flow: modular Bluetooth builds call the real `bt_selftest` during module initialization. Built-in Bluetooth runs selftests from `selftest.c` through a late initcall instead, so users of this header get a no-op inline. Builds without selftests also compile to the no-op inline.

State and persistence behavior: owns no state. It only controls whether a caller sees a real module-load selftest entry or a no-op.

Dependencies and integration points: depends on Kconfig symbols `CONFIG_BT_SELFTEST` and `CONFIG_BT`. It is included by Bluetooth core initialization code to keep module and built-in selftest paths distinct.

Risks: configuration logic must match `selftest.c`; otherwise module builds could miss real selftests or built-in builds could attempt to call an unavailable symbol. The no-op success return can hide lack of selftest coverage unless build configuration is inspected.

Test signals: compile Bluetooth as module and built-in with `CONFIG_BT_SELFTEST` enabled and disabled; verify module builds call the real function, built-in builds run the late initcall, and disabled builds have no selftest side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/selftest.h -->
