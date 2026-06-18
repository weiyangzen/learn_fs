## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.h

Purpose: declares the ath12k testmode interface and provides no-op inline stubs when `CONFIG_NL80211_TESTMODE` is disabled.

Important APIs/types: exposes `ath12k_tm_wmi_event_unsegmented()`, `ath12k_tm_process_event()`, and `ath12k_tm_cmd()` with forward use of `struct ath12k_base`, `struct ath12k_wmi_ftm_event`, `struct ieee80211_hw`, and `struct ieee80211_vif`.

Control flow: compile-time branching is the main behavior. When testmode is enabled, callers link to `testmode.c`; otherwise WMI event hooks become empty and the command hook returns success without doing work.

State and persistence: no state is owned here. The enabled implementation manipulates runtime driver state in `testmode.c`; the disabled path deliberately persists nothing.

Dependencies/integration: includes `core.h` and `hif.h` so callers can include this header from WMI/mac80211 paths without separately carrying core declarations. It is the integration boundary between cfg80211 testmode and firmware event handlers.

Risks: the disabled stub returning `0` can hide accidental command-path invocations in builds without testmode support. Any signature drift between enabled and disabled branches would break compile coverage.

Test signals: build both `CONFIG_NL80211_TESTMODE=y` and disabled configurations; verify WMI event paths compile and that disabled command invocations are harmless.
