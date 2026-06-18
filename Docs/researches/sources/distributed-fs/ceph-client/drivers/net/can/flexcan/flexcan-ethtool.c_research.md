# sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-ethtool.c

Purpose: this companion file exposes FlexCAN ethtool operations. It reports fixed RX/TX ring characteristics and provides one private flag, `rx-rtr`, that selects the receive implementation needed to support or drop remote-transmission-request frames depending on hardware capabilities.

Important APIs, types, and functions: `flexcan_get_ringparam()` reports mailbox counts, RX FIFO depth, and single-buffer TX. `flexcan_get_strings()`, `flexcan_get_sset_count()`, `flexcan_get_priv_flags()`, and `flexcan_set_priv_flags()` implement `ETH_SS_PRIV_FLAGS`. The exported `flexcan_ethtool_ops` also uses `ethtool_op_get_ts_info`. The private flag maps to `FLEXCAN_QUIRK_USE_RX_MAILBOX` through helpers in `flexcan.h`.

Control flow: ethtool ring queries read `struct flexcan_priv` and return `mb_count` maxima, RX pending as mailbox span or fixed FIFO depth six, and TX pending one. Private-flag reads call `flexcan_active_rx_rtr()`. Private-flag writes compute a new quirk set: enabling `rx-rtr` chooses mailbox mode when mailbox RTR is supported, otherwise FIFO if available, otherwise mailbox; disabling chooses mailbox mode when only mailbox RX is supported and FIFO otherwise. If the quirk set would change while the netdev is running, the operation fails with `-EBUSY`; otherwise it updates the private quirk copy.

State and persistence: the only changed state is `priv->devtype_data.quirks`, a per-device copy created at probe time. The setting is runtime state, not persisted to firmware or device tree. It affects the next open/start path because RX offload setup and chip initialization inspect `FLEXCAN_QUIRK_USE_RX_MAILBOX`.

Dependencies and integration points: it depends on `flexcan.h`, Linux ethtool private flags, and the core driver's `struct flexcan_priv` layout. Users interact through `ethtool --show-priv-flags` and `--set-priv-flags`; the core driver consumes the resulting quirk bit during open.

Risks: changing RX mode while up is blocked, but users may still be surprised that disabling `rx-rtr` can force mailbox mode on devices without FIFO support and logs that RTR frames cannot be received. The flag is capability-sensitive, so bad quirk definitions in the core file can expose impossible mode choices.

Test signals: verify `ethtool -g` reports mailbox/FIFO ring values, private flag count/string is stable, `rx-rtr` toggles only while the interface is down, subsequent interface open uses the selected RX mode, and devices without RX RTR support emit the informational warning when appropriate.
