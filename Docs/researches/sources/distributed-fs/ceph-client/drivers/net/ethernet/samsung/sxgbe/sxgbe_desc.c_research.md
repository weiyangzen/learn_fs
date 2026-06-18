# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_desc.c

Purpose: provides the SXGBE descriptor operation implementation for normal TX/RX descriptors and TX/RX context descriptors. It prepares descriptors for DMA ownership, packet lengths, checksums, TSO, VLAN tags, timestamps, and decodes RX writeback status into driver statistics and checksum status.

Important APIs: `sxgbe_get_desc_ops()` returns `desc_ops`. TX callbacks initialize, prepare, set owner, close, release, check last segment, read length, set timestamp, and manipulate TX context descriptor MSS/VLAN/timestamp fields. RX callbacks initialize descriptors, set/get owner, enable interrupt-on-completion, get frame length and first/last status, parse RX writeback status, parse RX context status, test timestamp validity, and return timestamp value.

Control flow: transmit setup fills bitfields in `tdes23.tx_rd_des23`; close marks last descriptor and interrupt-on-completion; ownership is handed to hardware by setting `own_bit`. Receive initialization sets ownership to hardware and optional interrupt mode. RX writeback first treats `err_summary` and `err_l2_type` as either L2 error or packet type, updates extended stats, adjusts checksum to `CHECKSUM_NONE` for IP header/payload checksum errors, then records L3/L4 packet type and filter counters. RX context status updates PTP/timestamp counters and timestamp retrieval combines low/high words.

State and persistence: functions mutate descriptor memory passed by queue code and update `struct sxgbe_extra_stats`; no global mutable state.

Dependencies and integration: depends on descriptor layouts in `sxgbe_desc.h`, stats and constants in `sxgbe_common.h`, DMA definitions, net checksum constants, and queue management in main driver code.

Risks: descriptor layouts are C bitfields matching hardware, making compiler packing and endian assumptions critical. `sxgbe_release_tx_desc()` zeroes the whole descriptor, so caller must restore buffer address before reuse. RX status logs invalid types with `pr_err`, which can be noisy on corrupted descriptors. Some status counters have naming inconsistencies (`dvan_ocvlan_icvlan_pkt` vs `dvlan...`) mirrored in ethtool.

Test signals: TX descriptor contents for linear, fragmented, TSO, VLAN, and timestamped packets; ownership transitions; RX error decoding for every `RX_*` status; checksum status on IP errors; PTP context descriptor timestamps; and ethtool stat increments.
