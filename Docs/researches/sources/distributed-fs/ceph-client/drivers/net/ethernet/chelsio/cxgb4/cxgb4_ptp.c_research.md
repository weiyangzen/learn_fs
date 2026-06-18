# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ptp.c

Purpose: implements Chelsio T5/T6 Precision Time Protocol support: packet classification for timestamping, firmware commands for RX/TX timestamp modes, and PHC operations registered with Linux `ptp_clock`.

Important APIs/functions: exports `cxgb4_ptp_init`, `cxgb4_ptp_stop`, `cxgb4_ptp_is_ptp_tx`, `cxgb4_ptp_is_ptp_rx`, `is_ptp_enabled`, `cxgb4_ptp_read_hwstamp`, `cxgb4_ptprx_timestamping`, `cxgb4_ptp_txtype`, and `cxgb4_ptp_redirect_rx_packet`; PHC callbacks include `cxgb4_ptp_adjfine`, `cxgb4_ptp_adjtime`, `cxgb4_ptp_gettime`, and `cxgb4_ptp_settime`.

Control flow: TX timestamp eligibility checks skb hardware timestamp flags and UDP/IPv4 PTP event-port packets. RX/TX mode functions build `FW_PTP_CMD` mailbox commands. PHC registration copies `cxgb4_ptp_clock_info`, initializes firmware timer state, sets PHC time to wall clock, and unregisters if settime fails. TX timestamp completion reads MAC timestamp registers, stamps `adapter->ptp_tx_skb`, frees it, and clears the pointer under `ptp_lock`.

State and persistence: adapter state includes `ptp_clock`, `ptp_clock_info`, `ptp_tx_skb`, and `ptp_lock`; hardware clock state is in MAC/PTP registers and firmware PTP timer settings. State is runtime-only and removed by `cxgb4_ptp_stop`.

Dependencies/integration: uses Linux PTP clock, skb timestamp, UDP/IP header, and net timestamp APIs plus Chelsio `t4_wr_mbox` and `t4_read_reg`. `cxgb4_main.c` initializes it for devices with PTP support.

Risks: `cxgb4_ptp_is_ptp_rx` manually offsets from skb data and assumes an Ethernet + IPv4 layout. `cxgb4_ptp_read_hwstamp` assumes `adapter->ptp_tx_skb` is valid before lock clearing. Large time adjustments use firmware `ADJ_TIME`, small ones use `ADJ_FTIME`, so edge cases around the 10 ms threshold need coverage.

Test signals: exercise `ethtool -T`, `phc2sys`/`ptp4l`, TX and RX hardware timestamp requests, negative and positive adjtime/adjfine operations, stop during pending TX timestamp, and firmware command failure injection.
