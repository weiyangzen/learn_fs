# sources/distributed-fs/ceph-client/include/linux/qed/qed_eth_if.h

Purpose: declares the public Ethernet client interface exported by the QED core to qede/netdev code, including device info, vport lifecycle, queue start/stop, filters, RSS, tunnel configuration, PTP, DCB, SR-IOV access, stats, and callbacks.

Important APIs/types/functions: queue structures include `qed_queue_start_common_params`, `qed_rxq_start_ret_params`, and `qed_txq_start_ret_params`. Device/vport/filter structures include `qed_dev_eth_info`, `qed_start_vport_params`, `qed_update_vport_params`, `qed_update_vport_rss_params`, `qed_filter_ucast_params`, `qed_filter_mcast_params`, `qed_tunn_params`, and `qed_ntuple_filter_params`. Enums cover filter config mode, RX mode, xcast operation type, filter type, and PTP filter/tx timestamp types. Callback/ops tables include `qed_eth_cb_ops`, optional `qed_eth_dcbnl_ops`, `qed_eth_ptp_ops`, and the top-level `qed_eth_ops`. Entry points are `qed_get_eth_ops()` and `qed_put_eth_ops()`.

Control flow: an Ethernet client gets ops, probes/common-starts the device, fills device info, registers callbacks, starts vports, starts RX/TX queues with status-block indices and PBL addresses, configures RSS/filters/tunnels/PTP/DCB as needed, handles slow-path RX CQE completions, gathers stats, then stops queues/vports and releases ops. Callback flow notifies the client about forced MACs, tunnel-port updates, link/DCBX/common events, and recovery.

State and persistence: this header defines contracts for runtime QED Ethernet state: vports, queues, RSS tables/keys, MAC/VLAN/multicast filters, ntuple/aRFS filters, tunnel ports, PTP timestamping, and stats. State persists in firmware until explicitly updated/stopped or reset; the header itself stores no state.

Dependencies and integration points: includes Linux list and if_link/DCB types, `eth_common.h`, `qed_if.h`, and `qed_iov_if.h`. Integrates QED with Linux netdev/qede, ethtool/DCB, PTP hardware timestamping, SR-IOV VF management, XDP capability reporting, tunnel offload configuration, and aRFS/searcher filters.

Risks: mismatched queue IDs/status-block indices, wrong PBL sizes, stale RSS pointer arrays, filter add/delete semantics, and VF-relative identifiers can misroute traffic. Optional DCB/SR-IOV function pointers depend on configs. PTP drift limit and timestamp filter selections need device support. aRFS header DMA buffers must be valid long enough for firmware consumption.

Test signals: qede open/close, MTU changes, RX/TX queue scaling, RSS indirection/key updates, VLAN/MAC/multicast/promiscuous filters, ntuple/aRFS add/remove/drop, tunnel port updates, PTP timestamp read/adjust/enable/disable, DCB operations under `CONFIG_DCB`, SR-IOV VF configuration, and stats consistency through ethtool.
