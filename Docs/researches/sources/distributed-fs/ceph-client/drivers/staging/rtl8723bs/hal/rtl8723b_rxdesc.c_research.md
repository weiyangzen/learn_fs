# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723b_rxdesc.c

Purpose: this small file updates user-visible receive signal statistics from parsed PHY information for RTL8723B receive frames.

Important APIs and functions: `rtl8723b_process_phy_info` is the exported entry point. It calls `process_rssi` and `process_link_qual`, which accumulate `SignalStrength` and `SignalQuality` from `rx_pkt_attrib.phy_info` into `recvpriv.signal_strength_data` and `recvpriv.signal_qual_data`.

Control flow: the SDIO receive tasklet parses RX descriptors and optional PHY status in `rtl8723bs_recv.c`. When PHY status belongs to a packet relevant to the current BSSID, self, beacon, or AP station, `update_recvframe_phyinfo` calls `rtl8723b_process_phy_info`. Each statistic resets its accumulator when `signal_stat.update_req` is set, then increments total count/value and recomputes an integer average.

State and persistence: state is purely in `recv_priv` signal statistic accumulators. There is no hardware access and no persistence outside adapter memory. The averages remain until reset by `update_req`, adapter teardown, or reinitialization.

Dependencies and integration: depends on `union recv_frame`, `rx_pkt_attrib`, and PHY parsing from ODM. It is tightly coupled to the receive tasklet selecting which frames should influence RSSI/link quality.

Risks and test signals: integer accumulation can grow over long sessions if `update_req` is not set by higher layers; there is no saturation. Because `process_rssi` lacks explicit null checks, callers must pass valid adapter/frame pointers. Tests should verify signal updates after beacon/self packets, AP-mode station packets, reset behavior when `update_req` is set, and no updates for CRC/ICV-dropped frames.
