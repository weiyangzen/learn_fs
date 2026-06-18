# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ptp.h

Purpose: this header declares the PTP and hardware timestamping interface used by the SFC core, datapath, ethtool timestamp reporting, and channel management code.

Important APIs: lifecycle functions are `efx_ptp_probe()`, `efx_ptp_defer_probe_with_channel()`, `efx_ptp_update_channel()`, `efx_ptp_channel()`, and `efx_ptp_remove()`. Configuration and reporting functions are `efx_ptp_set_ts_config()`, `efx_ptp_get_ts_config()`, and `efx_ptp_get_ts_info()`. Datapath hooks include `efx_ptp_is_ptp_tx()`, `efx_ptp_tx()`, `efx_ptp_event()`, `efx_time_sync_event()`, RX timestamp attach helpers, datapath start/stop, MAC TX timestamp capability, and `efx_ptp_nic_to_kernel_time()`.

Control flow and integration: normal RX delivery calls `efx_rx_skb_attach_timestamp()`, which only invokes the full attach path when channel sync events are valid. TX code can detect PTP packets and queue them for PTP handling. Event code routes PTP and time-sync events back to this module.

State and risks: the header exposes functions that assume `efx->ptp_data` may be absent, so callers must handle `-EOPNOTSUPP` or no-op behavior. The inline attach check depends on `channel->sync_events_state`. Test signals include compile coverage, timestamp config via `SIOCSHWTSTAMP`, TX/RX timestamping, and datapath restart.
