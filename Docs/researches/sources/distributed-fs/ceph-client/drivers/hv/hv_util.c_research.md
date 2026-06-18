<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_util.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_util.c

## Purpose

`hv_util.c` is the VMBus utility driver for Hyper-V integration components: shutdown, time synchronization, heartbeat, KVP, and VSS. It registers one `hv_driver` matching several utility GUIDs, opens utility channels in direct-read mode, delegates KVP/VSS to their modules, and implements shutdown, restart, hibernate, heartbeat, host time synchronization, and a read-only Hyper-V PTP clock.

## Important APIs, Types, and Functions

- `struct hv_util_service` instances `util_shutdown`, `util_timesynch`, `util_heartbeat`, `util_kvp`, and `util_vss` bind service callbacks and lifecycle hooks.
- `shutdown_onchannelcallback()` handles negotiation and shutdown/restart/hibernate host requests.
- `timesync_onchannelcallback()`, `adj_guesttime()`, `hv_get_adj_host_time()`, and `hv_set_host_time()` maintain host time samples and discipline guest time when requested.
- `heartbeat_onchannelcallback()` increments heartbeat sequence numbers and responds.
- `util_probe()`, `util_remove()`, `util_suspend()`, and `util_resume()` implement shared utility channel lifecycle.
- `hv_timesync_init()`, `hv_timesync_pre_suspend()`, and `hv_timesync_deinit()` manage work and PTP clock registration.
- `ptp_hyperv_info` exposes `gettime64` backed by the latest host time sample.

## Control Flow

Probe allocates a receive buffer, runs service-specific init, switches the channel to `HV_CALL_DIRECT`, stores driver data, opens the VMBus channel with utility-sized rings, and initializes optional userspace transport. Shutdown callbacks read one packet, negotiate if requested, otherwise inspect shutdown flags and schedule process-context poweroff, reboot, or hibernate uevent work after sending a host response. Timesync drains all available packets and uses the last host sample; version 4+ messages include a reference time for better precision. Heartbeat drains packets, negotiates or increments `seq_num`, and replies.

Suspend calls service-specific pre-suspend hooks, then closes the channel while userspace is frozen. Resume calls pre-resume hooks and reopens the channel. KVP and VSS hooks handle tasklet disable/enable and daemon state. Module init registers `hv_utils`; module exit unregisters it.

## State and Persistence Behavior

Each utility service has a persistent `recv_buffer` and channel pointer while probed. Shutdown keeps global hibernate work context and hibernation support state. Timesync stores the latest `host_time` and `ref_time` under `host_ts.lock`, plus a PTP clock pointer and adjustment work. Negotiated service versions are stored globally per service. Utility request buffers are reused for responses.

## Dependencies and Integration Points

This file depends on VMBus packet APIs, `vmbus_prep_negotiate_resp()` from `channel_mgmt.c`, KVP/VSS entry points from `hv_kvp.c` and `hv_snapshot.c`, `hv_read_reference_counter()` from `hv_common.c`, Linux reboot/poweroff, hibernation uevents, PTP clock APIs, and Hyper-V IC protocol structures.

## Risks and Edge Cases

Packet length checks are critical because host data is parsed in shared buffers. Timesync samples can become stale; PTP `gettime64` returns `-ESTALE` after a fixed threshold. `timesync_implicit` works around missing resume sync flags by forcing sync if guest time lags host. Shutdown work is scheduled only after the host response is sent. KVP can handle only one message at a time, which is why direct read mode is forced for all utility services.

## Test Signals

Test service negotiation for all GUIDs, shutdown/restart/hibernate requests, hibernation unsupported status, heartbeat sequence increment, timesync v3 and v4 samples, explicit and implicit clock sync, stale PTP reads, suspend/resume for all utility services, and KVP/VSS transport initialization failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_util.c -->
