# Research: sources/distributed-fs/ceph-client/net/mac80211/Kconfig

## sources/distributed-fs/ceph-client/net/mac80211/Kconfig

Purpose: Defines build-time configuration for the generic mac80211 IEEE 802.11 networking stack and its optional rate-control, mesh, LED, debugfs, tracing, KUnit, and debug features.

Important APIs/types/functions: Kconfig symbols include `MAC80211`, `MAC80211_HAS_RC`, `MAC80211_RC_MINSTREL`, the default rate-control choice and `MAC80211_RC_DEFAULT`, `MAC80211_KUNIT_TEST`, `MAC80211_MESH`, `MAC80211_LEDS`, `MAC80211_DEBUGFS`, `MAC80211_MESSAGE_TRACING`, `MAC80211_DEBUG_MENU`, many debug booleans for MLME/STA/HT/OCB/IBSS/powersave/mesh/TDLS, `MAC80211_DEBUG_COUNTERS`, and `MAC80211_STA_HASH_MAX_SIZE`.

Control flow: Selecting `MAC80211` depends on `CFG80211` and selects cryptographic and CRC primitives required by 802.11 security and frame handling. If mac80211 is enabled, rate-control support can select Minstrel and set `"minstrel_ht"` as the default. Optional features are gated by dependencies such as `KUNIT`, `LEDS_CLASS`, `CFG80211_DEBUGFS`, `TRACING`, `MAC80211_MESH`, and the debug menu.

State and persistence behavior: This file does not create runtime state; it shapes build artifacts, module availability, selected object compilation, defaults, and visible configuration prompts. The string `MAC80211_RC_DEFAULT` persists into build configuration and can influence runtime default rate-control selection unless overridden by module parameters.

Dependencies and integration points: Integrates with the Linux Kconfig system and the broader wireless stack. Driver Kconfigs can depend on or select mac80211-related symbols; debug and test symbols control compilation of additional instrumentation and KUnit suites.

Risks and test signals: Dependency mistakes can hide required options or allow builds without required crypto/rate-control support. Debug options are explicitly warned as unsuitable for production due to overhead and remotely triggerable logging. Test signals include `make olddefconfig`, dependency visibility checks with `CFG80211=n`, allmodconfig/allnoconfig coverage, KUnit build with `MAC80211_KUNIT_TEST`, and verifying mesh-only debug symbols appear only when mesh support is enabled.
