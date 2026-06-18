# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.h

Purpose: Declares WFx debug and trace-name helper APIs.

Important APIs and types: Exports `wfx_get_hif_name()`, `wfx_get_mib_name()`, `wfx_get_reg_name()`, and `wfx_debug_init()`.

Control flow and integration: HIF command error logging uses HIF/MIB names, tracepoints use register names, and common probe calls `wfx_debug_init()` after successful `ieee80211_register_hw()`.

State and persistence: No state is declared; debugfs state is implementation-private in `debug.c`.

Dependencies: Depends on `struct wfx_dev` and debugfs availability through implementation includes.

Risks and test signals: Build and runtime tests should verify debugfs initialization failure unwinds mac80211 registration and name helpers return fallback strings for unknown IDs.

Test signals: Source read size: 19 lines, 419 bytes.
