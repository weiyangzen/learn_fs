# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.h

`otx2_ptp.h` declares the PTP lifecycle/query API and inline timestamp format converters. `otx2_ptp_convert_rx_timestamp` converts OTX2 RX timestamps from big-endian 64-bit hardware layout, `otx2_ptp_convert_tx_timestamp` returns OTX2 TX timestamps unchanged, and `cn10k_ptp_convert_timestamp` converts a seconds:nanoseconds split where upper 32 bits are seconds and lower 32 bits are nanoseconds.

Declared APIs are `otx2_ptp_init`, `otx2_ptp_destroy`, `otx2_ptp_clock_index`, and `otx2_ptp_tstamp2time`. `otx2_ptp.c` assigns the converter callbacks by silicon generation, allowing packet paths to convert timestamps without repeatedly branching on device type.

The header has no mutable state. It depends on endian helpers, `NSEC_PER_SEC`, and forward availability of `struct otx2_nic` through include order. Risks are silent time errors if hardware timestamp formats change or if the big-endian RX cast is used on an unexpected layout. Test RX/TX hardware timestamps against PHC time on OTX2 and CN10K, including one-step TX mode where available.
