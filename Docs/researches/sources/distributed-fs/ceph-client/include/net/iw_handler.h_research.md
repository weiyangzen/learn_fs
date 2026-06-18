# sources/distributed-fs/ceph-client/include/net/iw_handler.h

Purpose: Defines the kernel-only Wireless Extensions handler API used by legacy wireless drivers to expose ioctl handlers, request metadata, ioctl descriptions, spy data, and event stream helpers.

Important APIs/types/functions: `iw_request_info` carries command and flags such as compat ioctl mode. `iw_handler` is the generic handler signature. `iw_handler_def` lists standard and optional private handler arrays, private argument descriptions, and a `get_wireless_stats` hook. `iw_ioctl_description` describes header type, copy token size, min/max tokens, and flags such as event/restrict/no-max. `iw_spy_data` stores spy addresses, quality, and thresholds. APIs include `wireless_send_event`, optional `wireless_nlevent_flush`, and event stream add/check helpers.

Control flow: The wireless core validates/copies ioctl payloads using description metadata, indexes handler arrays by ioctl number, calls driver handlers, and interprets `EIWCOMMIT` as a delayed commit request. Event helpers append fixed events, point events, or values into caller-provided streams and compat-adjust lengths when needed.

State and persistence: Driver-owned static `iw_handler_def` describes capabilities. Per-device spy data and statistics are driver/device state. This header carries no global mutable state except external event flushing.

Dependencies/integration: Depends on `linux/wireless.h`, net_device, Ethernet address constants, compat event lengths, and net/wireless core implementation.

Risks: Legacy ioctl pointer/copy semantics are vulnerable if description metadata is wrong; compat 32/64 event sizes must be correct to avoid leaking kernel memory; private handler arrays can be misindexed. Test signals include standard/private ioctl dispatch, compat events, event truncation returning `-E2BIG`, spy threshold events, restricted GET permissions, and `EIWCOMMIT` handling.
