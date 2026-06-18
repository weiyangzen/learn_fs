# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_ptp.c

## Purpose

`gve_ptp.c` provides minimal PTP clock integration for the NIC timestamp counter used by RX hardware timestamping and XDP RX timestamp metadata. It registers a PHC, periodically reads the NIC timestamp through adminq, and stores the latest raw counter for expansion of 32-bit RX timestamps in `gve_rx_dqo.c`.

## Important APIs, types, and functions

- `GVE_NIC_TS_SYNC_INTERVAL_MS`: schedules timestamp calibration every 250 ms.
- `gve_clock_nic_ts_read`: asks adminq to write a coherent NIC timestamp report, converts it from big endian, and updates `priv->last_sync_nic_counter`.
- `gve_ptp_do_aux_work`: periodic PTP worker that skips reads during reset or adminq failure and reschedules itself.
- `gve_ptp_init`, `gve_ptp_release`: allocate/register and unregister/free `struct gve_ptp`.
- `gve_init_clock`: initializes PTP, allocates the coherent `gve_nic_ts_report`, performs an initial timestamp read, and starts the worker.
- `gve_teardown_clock`: unregisters PTP and frees the timestamp report buffer.

## Control flow and state

When device resources are set up and NIC timestamping is supported, `gve_setup_device_resources()` calls `gve_init_clock()`. The clock path registers a PTP clock whose set/get time operations currently return `-EOPNOTSUPP`; its useful operation is auxiliary work. The coherent timestamp report buffer and `last_sync_nic_counter` persist while device resources are active and are freed on teardown/reset.

## Dependencies and integration points

The file depends on adminq `gve_adminq_report_nic_ts()`, Linux PTP clock APIs, DMA coherent allocation, and reset/adminq state helpers. `gve_rx_dqo.c` consumes `last_sync_nic_counter` to expand per-packet hardware timestamps. `gve_ethtool.c` reports timestamp capabilities and PHC index when the clock is enabled.

## Risks and test signals

Risks include stale timestamp calibration if aux work is blocked too long, invalid RX timestamp expansion when packet time differs from the last sync by more than the documented range, PTP registration failure fallback, and teardown races with scheduled aux work. Tests should check clock init/teardown fault paths, ethtool timestamp info, RX timestamp validity before/after reset, adminq timestamp read failures, and behavior when NIC timestamp support is absent.
