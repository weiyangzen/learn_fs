# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-dvb.c

Purpose: Registers FireDTV as a DVB adapter/demux/frontend/network device and maps demux feed start/stop events to FireDTV PID filter AV/C commands.

Important APIs/types/functions: Channel helpers `alloc_channel()`, `collect_channels()`, and `dealloc_channel()` manage up to 16 hardware PID channels using `fdtv->channel_active` and `channel_pid`. Public demux callbacks are `fdtv_start_feed()` and `fdtv_stop_feed()`. `fdtv_dvb_register()` creates the DVB adapter, demux, dmxdev, memory/frontend connection, DVB net, frontend, and optional CA device. `fdtv_dvb_unregister()` tears them down.

Control flow: Feed start validates demux feed type and PES type, takes `demux_mutex`, allocates a channel, records the PID, collects all active PIDs, and either requests full TS for PID 8192 or programs the current PID set with `avc_tuner_set_pids()`. Feed stop handles DVB core decoder bookkeeping, clears the channel, recollects PIDs, and updates the device filters. DVB registration performs staged setup with failure labels unwinding in reverse order; unregister mirrors successful setup.

State and persistence: Runtime state includes DVB adapter/demux objects, `demux_mutex`, active-channel bitmap, per-channel PID array, adapter module option `adapter_nr`, and CA registration state. No persistent storage exists.

Dependencies/integration: Depends on DVB core, demux, dmxdev, dvbnet, FireDTV frontend/CA/AVC helpers, and `firedtv.h`. It is called by the FireWire probe/remove path in `firedtv-fw.c`.

Risks and test signals: Test all registration failure labels, adapter numbering, 16-channel exhaustion, PID 8192 full-TS path, section and TS feed types, invalid PES/feed type rejection, start error rollback, stop with decoder/non-packet feeds, and concurrent feed operations. The code relies on feed-private channel indices remaining valid and on `demux_mutex` covering PID bitmap updates.
