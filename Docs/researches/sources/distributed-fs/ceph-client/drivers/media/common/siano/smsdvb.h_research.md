<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h

## Purpose
`smsdvb.h` defines the per-DVB-client state and debugfs callback interface for the Siano DVB adaptation layer. It also documents the special per-slice reception-statistics structure used by firmware indications.

## Important APIs, Types, and Functions
The main type is `struct smsdvb_client_t`, which embeds DVB adapter, demux, dmxdev, and frontend objects alongside Siano core client pointers, frontend status, completions, legacy statistics, board-event state, statistics throttling, feed counters, tune state, and optional debugfs fields.

It defines callback typedefs for DVB, ISDB-T, and extended ISDB-T stats printers. `struct RECEPTION_STATISTICS_PER_SLICES_S` models the payload of `MSG_SMS_HO_PER_SLICES_IND` and combines fields from older Siano statistics types. The header declares debugfs functions when `CONFIG_SMS_SIANO_DEBUGFS` is enabled and provides no-op stubs otherwise.

## Control Flow
`smsdvb-main.c` allocates and fills `smsdvb_client_t` during hotplug. Incoming firmware statistics are converted and optionally passed through the callback pointers declared here. Debugfs creation installs these callback pointers; debugfs release clears them before removing files.

## State and Persistence Behavior
The header describes volatile runtime state only. `feed_users` and `has_tuned` gate TS demux delivery. `get_stats_jiffies` throttles statistics polling. `event_fe_state` and `event_unc_state` suppress repeated board notifications. Debugfs pointers are valid only while the optional debugfs node exists.

## Dependencies and Integration Points
This header relies on DVB types, `smscore_device_t`, `smscore_client_t`, and Siano statistics structures from `smscoreapi.h`. Its config stubs let `smsdvb-main.c` call debugfs hooks unconditionally while keeping debugfs optional.

## Risks and Test Signals
Because this header owns embedded DVB objects, lifetime order in `smsdvb-main.c` must match allocation and registration order. The stats callback pointers must be null-checked by callers before use, as the debugfs module can be disabled or released. Test signals include successful builds with and without `CONFIG_SMS_SIANO_DEBUGFS` and correct initialization of completions and event state before frontend use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h -->
