# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Kconfig

Purpose: Top-level Kconfig menu for Atheros/Qualcomm wireless drivers. It gates vendor visibility, declares common debug/regulatory feature switches, and sources all per-driver Atheros family Kconfig files.

Important APIs/types/functions: Defines `ATH_COMMON` as a tristate selected by individual drivers, `WLAN_VENDOR_ATH` as the visible vendor menu, and feature booleans `ATH_DEBUG`, `ATH_TRACEPOINTS`, `ATH_REG_DYNAMIC_USER_REG_HINTS`, and `ATH_REG_DYNAMIC_USER_CERT_TESTING`. The file then includes `ath5k`, `ath9k`, `carl9170`, `ath6kl`, `ar5523`, `wil6210`, `ath10k`, `wcn36xx`, `ath11k`, and `ath12k` configuration trees.

Control flow: Kernel configuration first asks whether to show the vendor menu. When enabled, the debug/regulatory options are exposed, then child Kconfig files provide concrete driver selections. `ATH_TRACEPOINTS` depends on both `ATH_DEBUG` and `EVENT_TRACING`; the dynamic regulatory options require `CFG80211_CERTIFICATION_ONUS`.

State/persistence: The only persisted state is the generated kernel `.config`, which determines which modules and feature objects are built. There is no runtime state.

Dependencies/integration: Integrates with cfg80211/mac80211 regulatory policy, the kernel event tracing subsystem, and downstream Atheros driver directories. `ATH_COMMON` corresponds to the common object built by the adjacent Makefile.

Risks: Regulatory options are intentionally warned as "Say N"; enabling them incorrectly can allow user regulatory hints or certification behavior outside permitted environments. Debug and trace options can increase binary size and expose additional diagnostics.

Test signals: Kconfig coverage is validated by `olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted builds that select individual Atheros drivers and ensure dependencies pull in `ATH_COMMON` and tracing/debug objects as expected.
