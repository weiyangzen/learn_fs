# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ptp.c

`otx2_ptp.c` implements Precision Time Protocol PHC support. It registers a `ptp_clock`, provides adjustment/get/set callbacks, supports external timestamp polling and periodic output, chooses hardware-atomic or software timecounter conversion based on firmware capability, and exposes timestamp conversion helpers for netdev timestamp paths.

Exported APIs are `otx2_ptp_init`, `otx2_ptp_destroy`, `otx2_ptp_clock_index`, and `otx2_ptp_tstamp2time`. PTP callbacks include `otx2_ptp_adjfine`, `otx2_ptp_enable`, `otx2_ptp_verify_pin`, hardware get/set/adjtime callbacks, and timecounter get/set/adjtime callbacks. Mailbox helpers issue `PTP_OP_GET_CLOCK`, `PTP_OP_GET_TSTMP`, `PTP_OP_SET_THRESH`, `PTP_OP_PPS_ON`, and related operations.

Initialization skips loopback VFs, probes PTP availability, allocates `struct otx2_ptp`, fills `ptp_clock_info`, queries `PTP_CAP_HW_ATOMIC_UPDATE`, either wires callbacks directly to hardware mailbox operations or initializes `cyclecounter/timecounter`, registers the PHC, and selects OTX2 or CN10K timestamp converters. Delayed work polls external timestamp state and maintains one-step sync timestamp cache.

State lives in `pfvf->ptp`: PHC pointer, counters, delayed works, last external timestamp, threshold, pin config, converter callbacks, cached timestamp, and base nanoseconds. Dependencies include Linux PTP/timecounter APIs, AF PTP mailbox operations, `otx2_ptp.h`, and hwtstamp/ethtool integration in PF code.

Risks include mixed lock ownership around mailbox helpers, zero timestamps on read failure, delayed-work teardown ordering, and `extts_work` lifetime during destroy. Test `ptp4l/phc2sys`, `ethtool -T`, get/set/adj operations, external timestamp enable/disable, periodic output, one-step TX mode, OTX2/CN10K conversion, and removal while EXTS is active.
