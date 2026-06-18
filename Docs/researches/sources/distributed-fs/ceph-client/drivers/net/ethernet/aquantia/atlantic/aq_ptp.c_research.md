<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c

Purpose: implements Linux PTP hardware clock support for capable Atlantic A1/B0-era devices, including clock adjustment, hardware timestamp TX/RX rings, timestamp filters, GPIO periodic output/external timestamp support, and timeout cleanup.

Important APIs/functions: exported functions include `aq_ptp_init`, `aq_ptp_ring_alloc/init/start/stop/deinit/free`, `aq_ptp_irq_alloc/free`, `aq_ptp_xmit`, `aq_ptp_tx_hwtstamp`, `aq_ptp_hwtstamp_config_set/get`, `aq_ptp_extract_ts`, `aq_ptp_link_change`, and stats helpers. Internal types include `struct aq_ptp_s`, `ptp_skb_ring`, and `ptp_tx_timeout`.

Control flow: init checks chip feature, hardware timestamp ops, firmware `enable_ptp`, and firmware-reported PHY PTP capability; it loads per-speed offsets, registers a PTP clock, creates NAPI, enables firmware PTP, and reserves filters. Ring allocation creates PTP TX/RX plus hardware timestamp RX rings and an skb queue. PTP NAPI cleans TX completions, timestamp completions, and RX traffic. HWTSTAMP configuration programs UDP/L2 filters into the dedicated PTP RX queue.

State and persistence: `aq_ptp_s` stores hwtstamp config, spinlocks, PTP clock info, offset atomics, rings, pending skb timestamp queue, reserved filters, delayed GPIO polling work, and last sync timestamp. Hardware/firmware PTP state is enabled/disabled through ops.

Dependencies and integration: depends on Linux `ptp_clock_kernel`, packet timestamping, NAPI, IRQ, `aq_ring`, `aq_phy`, and `aq_filters`. B0 hardware provides most PTP ops.

Risks: pending TX timestamp SKBs can overflow or timeout; filter programming failures return remote I/O errors; GPIO external timestamp polling samples multiple times to avoid unstable reads; PTP is disabled when TC count exceeds hardware PTP TC limits. Test signals include `ptp4l`/`phc2sys`, `SIOCSHWTSTAMP`, TX timeout logs, PTP RX filter routing, GPIO perout/extts, link changes, and disabled Kconfig stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.c -->
