# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.h

Purpose: Declares channel, interrupt, event queue, NAPI, and queue-stat helper APIs shared between core probe/reset code and datapath code.

Important APIs: Exposes interrupt probe/remove/enable/disable, affinity helpers, eventq lifecycle, channel allocation/probe/remove/reallocation/start/stop, NAPI lifecycle, `efx_get_queue_stat_rx_hw_drops()`, and `efx_channel_dummy_op_void()`. Declares module parameters `efx_interrupt_mode` and `rss_cpus`.

Control flow and integration: Core `efx.c` and `efx_common.c` call these functions during probe, open, stop, reset, PM, and removal. The inline RX hardware-drop helper sums channel drop/error counters for stats.

State and persistence: Header owns no state but exposes operations that mutate NIC channel topology, IRQ mode, NAPI state, and queue stats.

Dependencies: Requires `struct efx_nic` and `struct efx_channel` from shared driver headers and implementation in `efx_channels.c`.

Risks: Callers must respect lifecycle ordering: probe before init/start, stop before remove, disable interrupts before teardown. Drop counter composition must stay aligned with RX paths that increment those counters.

Test signals: Compile lifecycle users, verify stats include CRC, truncation, overlength, nodesc, and bad-mport drops, and exercise reset/open/close paths that call channel start/stop.
