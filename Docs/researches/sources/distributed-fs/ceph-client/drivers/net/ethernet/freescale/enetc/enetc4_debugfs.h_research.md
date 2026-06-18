# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.h

Purpose: Declares ENETC4 debugfs creation/removal helpers and provides no-op inline stubs when debugfs is disabled.

Important APIs: `enetc_create_debugfs(struct enetc_si *si)` and `enetc_remove_debugfs(struct enetc_si *si)` are real functions under `CONFIG_DEBUG_FS`; otherwise they compile to empty inline functions.

Control flow and state: The header itself has no runtime state. It lets ENETC4 PF code call debugfs setup/teardown unconditionally without sprinkling `#ifdef CONFIG_DEBUG_FS` through caller code.

Dependencies and integration points: Expects `struct enetc_si` to be visible or at least forward-declared by includers. Integrates with `enetc4_debugfs.c` and the ENETC4 PF lifecycle.

Risks: If included before `struct enetc_si` is declared in a context that needs prototype checking, build errors are possible; current local include ordering should avoid that. The disabled-debugfs stubs intentionally hide missing debugfs behavior, so tests must run with `CONFIG_DEBUG_FS=y` to exercise the real path.

Test signals: Build with DEBUG_FS enabled and disabled, and ENETC4 PF probe/remove tests that call the helpers in both configurations.
