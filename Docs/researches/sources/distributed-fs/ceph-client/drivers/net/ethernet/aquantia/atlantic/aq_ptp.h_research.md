<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h

Purpose: declares the PTP interface used by the NIC, ring, ethtool/timestamp, and hardware paths, with no-op stubs when PTP clock support is unavailable.

Important APIs/types: defines dedicated ring indices (`PTP_8TC_RING_IDX`, `PTP_4TC_RING_IDX`, `PTP_HWST_RING_IDX`) and `aq_ptp_ring_idx`. Declares init/free, IRQ, ring lifecycle, service, clock init, TX/RX timestamp, hwtstamp config, ring identification, link-change, and PTP stats helpers.

Control flow: generic NIC code calls these hooks unconditionally, relying on inline stubs under `!CONFIG_PTP_1588_CLOCK`. Runtime-capable builds allocate and start PTP resources alongside normal rings, and ring RX code calls `aq_ptp_ring`/`aq_ptp_extract_ts` for timestamp-aware packets.

State and persistence: no header state; implementation state is opaque `struct aq_ptp_s` referenced from `aq_nic_s`.

Dependencies and integration: includes Linux timestamp config and `aq_ring`; bridges netdev timestamping, ring receive, and hardware timestamp extraction.

Risks: callers must check availability when dereferencing `aq_ptp_s`; ring index constants must remain compatible with TC mode and hardware ring count; stubs must preserve behavior for non-PTP builds. Test signals include compile tests with PTP enabled/disabled and runtime hwtstamp ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ptp.h -->
