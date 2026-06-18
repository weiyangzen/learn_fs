<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c

## Purpose
`testmode.c` implements nl80211 testmode plumbing for ath6kl. It accepts userspace test commands, forwards TCMD payloads to firmware through WMI, and emits firmware testmode events back to userspace.

## Important APIs, Types, And Functions
Local enums define netlink attributes `ATH6KL_TM_ATTR_CMD` and `ATH6KL_TM_ATTR_DATA`, commands `ATH6KL_TM_CMD_TCMD` and obsolete `ATH6KL_TM_CMD_RX_REPORT`, and a 5000-byte data limit. `ath6kl_tm_policy[]` validates command and binary payload attributes.

`ath6kl_tm_cmd()` parses a cfg80211 testmode request, requires `ATH6KL_TM_ATTR_CMD`, supports only `ATH6KL_TM_CMD_TCMD`, requires binary data, and calls `ath6kl_wmi_test_cmd(ar->wmi, buf, buf_len)`. `ath6kl_tm_rx_event()` allocates a cfg80211 testmode event skb, attaches command and payload attributes, and sends it with `cfg80211_testmode_event()`.

## Control Flow
Userspace sends a testmode netlink command to cfg80211. cfg80211 invokes ath6kl’s testmode op, which parses attributes and either forwards the payload to firmware or rejects unsupported commands. Firmware-originated testmode data is passed to `ath6kl_tm_rx_event()`, wrapped in the same command/data attribute format, and published as a cfg80211 testmode event.

## State And Persistence
This file stores no long-lived driver state. It uses `wiphy_priv()` to recover `struct ath6kl` and transient sk_buffs for event emission.

## Dependencies And Integration Points
It depends on cfg80211 testmode support, netlink attribute APIs, `ath6kl_wmi_test_cmd()`, `testmode.h`, and debug warnings. It is meaningful only when the driver was booted with testmode firmware selected in `init.c`.

## Risks
`ath6kl_tm_cmd()` does not propagate the return value of `ath6kl_wmi_test_cmd()`, so command transport failures may be invisible to userspace. Payload length is bounded by netlink policy but command semantics are firmware-defined. The obsolete RX report command is intentionally unsupported; userspace tools must use TCMD.

## Test Signals
Signals include netlink parse errors, `-EINVAL` for missing attributes, `-EOPNOTSUPP` for unknown commands, successful cfg80211 testmode events, and firmware TCMD responses. Tests should include maximum-size payloads, zero-length/missing data, unsupported commands, and event allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c -->
