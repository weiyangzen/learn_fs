# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-dvb.c

## Purpose
Implements AU0828 digital TV support: frontend/tuner attachment, DVB adapter/demux/net registration, bulk URB transport, stream restart workaround, and DVB suspend/resume.

## Important APIs, types, and functions
Board-specific configs cover AU8522 demod, LED thresholds, XC5000, MXL5007T, and TDA18271 tuners. `urb_completion()` validates bulk packets, checks TS sync byte `0x47`, feeds packets via `dvb_dmx_swfilter_packets()`, and resubmits. `start_urb_transfer()` and `stop_urb_transfer()` allocate/submit or kill/free `URB_COUNT` bulk URBs. `au0828_dvb_start_feed()` and `au0828_dvb_stop_feed()` reference-count demux feeding and start/stop bridge transport registers. `au0828_restart_dvb_streaming()` handles timeout/misalignment restart. `au0828_set_frontend()` wraps frontend tuning so streaming stops before tuning and restarts after. `dvb_register()` registers adapter, frontend, demux frontends, dmxdev, net, and media graph. `au0828_dvb_register()` attaches board-specific frontend/tuner.

## Control flow and state
DVB registration attaches hardware based on `boardnr`, then registers DVB core objects. First active feed starts transport and URBs; last feed cancels restart work, stops URBs, and stops transport. Timeout or bad TS alignment schedules restart work. Suspend stops active streams and remembers `need_urb_start`; resume resumes frontend and restarts transport if needed.

## Dependencies and integration points
Depends on DVB core, AU8522, XC5000, MXL5007T, TDA18271, media-controller DVB graph support, and AU0828 bridge register writes.

## Risks and test signals
Risks include URB allocation unwind leaks, bad sync-byte false positives on short/corrupt data, restart work racing with stop/tune, and preallocated buffer lifetime. Test signals include DVB scan/lock, packet counters, restart on induced misalignment, feed reference-count balance, suspend/resume with active feed, and clean unregister freeing all DVB objects.
