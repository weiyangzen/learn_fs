<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c

Purpose: Implements the carl9170 receive side for firmware command traps, USB RX stream framing, 802.11 MPDU status decoding, power-save beacon observation, and BlockAck/BAR side effects.

Important APIs/types/functions: Exports `carl9170_rx()` and `carl9170_handle_command_response()`. Internal entry points include `carl9170_rx_stream()`, `__carl9170_rx()`, `carl9170_rx_untie_cmds()`, `carl9170_rx_untie_data()`, `carl9170_rx_mac_status()`, `carl9170_rx_phy_status()`, `carl9170_ps_beacon()`, and `carl9170_ba_check()`. It consumes `struct ar9170_rx_head`, `struct ar9170_rx_phystatus`, `struct ar9170_rx_macstatus`, and `struct carl9170_rsp`.

Control flow: USB completions pass buffers to `carl9170_rx()`. Stream-enabled firmware is split by `AR9170_RX_STREAM_TAG`; non-stream frames are classified by the repeated `0xffff` command marker. Command traps validate monotonic firmware sequence numbers, dispatch PRETBTT/TXCOMP/WATCHDOG/TEXT/GPIO/BOOT events, and complete synchronous command waiters. Data frames are decoded as single or A-MPDU first/middle/last MPDUs, with PLCP cached for aggregate members, then copied into a fresh skb and delivered through `ieee80211_rx()`.

State and persistence: Updates in-memory driver state only: `cmd_seq`, firmware error counters, power-save timestamps/overrides, `rx_plcp`, `rx_has_plcp`, `ampdu_ref`, RX drop counters, BAR tracking lists, and stream failover skb/missing-byte state. No durable persistence.

Dependencies and integration points: Integrates with mac80211 RX status fields, firmware command protocol, TX status processing, beacon update logic, WPS input reporting, RCU-protected vif/BA lists, and `ath_is_mybeacon()`.

Risks and test signals: Main risks are malformed USB stream repair, sequence loss causing restarts, A-MPDU ordering assumptions, copied skb allocation failures, and status/rate decoding mismatches. Useful signals include RX under load, firmware trap loss logs, FCS/PLCP filter behavior, suspend/restart recovery, PS beacon handling, and BlockAck acknowledgment of BAR frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/rx.c -->
