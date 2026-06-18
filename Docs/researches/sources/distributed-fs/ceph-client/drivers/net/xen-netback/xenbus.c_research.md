# sources/distributed-fs/ceph-client/drivers/net/xen-netback/xenbus.c

Purpose: Provides the Xenbus control plane for netback. It advertises backend features, creates VIF devices, watches frontend state and configuration, connects rings/event channels, manages hotplug-status deferral, and tears down queues on disconnect.

Important APIs, types, and functions: `netback_probe()` publishes feature keys and creates `backend_info`; `frontend_changed()` maps frontend Xenbus states into backend transitions; `connect()` reads negotiated features, allocates queues, registers watchers, and connects control/data rings; `connect_data_rings()` reads ring refs and event channels; `read_xenbus_vif_flags()` imports frontend offload capabilities; `set_backend_state()` enforces the allowed backend state graph. Debugfs helpers expose ring state and a manual kick.

Control flow: Probe writes backend feature keys in XenStore, switches to `InitWait`, reads hotplug script configuration, and creates the VIF. When the frontend reaches `Connected`, `connect()` validates queue count, reads MAC/rate/features, maps optional control ring, allocates per-queue state, connects each data ring, sets real queue counts, turns carrier on, registers the hotplug-status watch, and wakes TX queues. Closing states call `backend_disconnect()` and move through `Closing` to `Closed`.

State and persistence behavior: XenStore holds negotiated feature and ring keys, rate limits, hotplug status, and frontend/backend states. Runtime state lives in `backend_info`, `xenvif`, watchers, debugfs dentries, hotplug script string, and queue allocations. Reconnect destroys and recreates volatile queue/ring state.

Dependencies and integration points: Integrates Xenbus transactions/watches, XenStore, Linux hotplug uevents, debugfs, RTNL queue count updates, and the data/control connection helpers in `interface.c` and `netback.c`.

Risks: XenStore is frontend-controlled in several places, so queue count, ring refs, event channels, MAC strings, and feature flags need strict validation. Partial failures must unwind already-created queues and the control ring. Hotplug-status deferral can leave state changes pending. Watch callbacks may race disconnect without proper unregistering.

Test signals: Probe/remove with hotplug scripts, frontend state machine transitions, malformed MAC/rate/queue values, single versus multi-queue paths, split versus shared event channels, optional control ring absent/present, feature negotiation combinations, watcher updates for rate and multicast control, debugfs kick/read, and backend restart/reconnect.
