<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c

## Purpose
`smsdvb-main.c` adapts a Siano core device into Linux DVB devices. It registers a core hotplug callback, creates a DVB adapter/demux/dmxdev/frontend per arriving Siano device, maps DVB frontend operations into Siano firmware control messages, feeds transport-stream packets into the DVB demux, and converts firmware statistics into DVB property-cache metrics and legacy frontend reads.

## Important APIs, Types, and Functions
The file uses `struct smsdvb_client_t` from `smsdvb.h` as the per-adapter state. Important functions include `smsdvb_hotplug()`, `smsdvb_unregister_client()`, `smsdvb_onresponse()`, feed control (`smsdvb_start_feed()`, `smsdvb_stop_feed()`), statistics request/read helpers, frontend tuning (`smsdvb_dvbt_set_frontend()`, `smsdvb_isdbt_set_frontend()`, `smsdvb_set_frontend()`), frontend power callbacks, statistics translators, and module init/exit.

`smsdvb_fe_ops` advertises a "Siano Mobile Digital MDTV Receiver" frontend with DVB-T-like capabilities; delivery system is set to DVB-T or ISDB-T at registration based on the core mode.

## Control Flow
At module load, `smsdvb_module_init()` registers debugfs and the `smsdvb_hotplug()` callback with the core. For each arriving device, `smsdvb_hotplug()` allocates a client, registers a DVB adapter, initializes demux and dmxdev, copies frontend ops, registers the frontend, registers a Siano core client for `MSG_SMS_DVBT_BDA_DATA`, initializes completions, inserts the client in a global list, emits board hotplug/setup events, creates debugfs, and creates a media graph.

Frontend tuning clears status and stats, then dispatches to DVB-T or ISDB-T tuning based on core mode. DVB-T sends `MSG_SMS_RF_TUNE_REQ` with frequency, bandwidth enum, and 12 MHz crystal. ISDB-T sends `MSG_SMS_ISDBT_TUNE_REQ` with frequency, segment bandwidth, crystal, and segment index. Both paths try tuning with board LNA off first, read status, and retry with LNA enabled if needed.

Incoming messages are handled by `smsdvb_onresponse()`. TS data is passed to `dvb_dmx_swfilter()` only when feeds exist and the frontend has tuned. Tune responses complete `tune_done`. Signal/statistics indications update status/property caches, trigger board LED/event state, complete `stats_done`, and mark `has_tuned`.

## State and Persistence Behavior
Per-client state includes DVB adapter/demux/frontend objects, tune/stat completions, current `fe_status`, legacy BER/PER, frontend/uncorrected event state, throttling jiffies for statistics requests, feed user count, and `has_tuned`. Global state is a list of live DVB clients protected by `g_smsdvb_clientslock`. There is no disk persistence; state is rebuilt on hotplug.

## Dependencies and Integration Points
The file integrates the Siano core client API, board control helpers from `sms-cards`, Linux DVB adapter/demux/frontend APIs, media-controller graph creation, and optional debugfs callbacks. It depends on firmware message ids and statistics layouts from `smscoreapi.h`.

## Risks and Test Signals
Risk areas include concurrent feed start/stop updating `feed_users` without a local lock, statistics request throttling returning cached state, timeout behavior of `smsdvb_sendrequest_and_wait()`, and the LNA retune sequence changing board state. `smsdvb_read_signal_strength()` reads `power` before requesting fresh statistics, so the returned value may reflect the previous cached sample.

Test signals include successful DVB adapter/frontend registration after Siano hotplug, PID add/remove messages on demux feed changes, TS demux activity only after tune lock, frontend status transitions through board events, statistics properties using FE_SCALE_COUNTER/DECIBEL as expected, module unload releasing clients cleanly, and media graph creation success under media-controller builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c -->
