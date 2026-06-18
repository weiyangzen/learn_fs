# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.c

## Purpose
Provides the AS102 DVB-layer integration and module entry point. It bridges DVB demux/frontend callbacks to AS10x firmware commands and USB private operations supplied by `as102_usb_drv.c`.

## Important APIs, types, and functions
Module parameters are `dual_tuner`, `fw_upload`, `pid_filtering`, `ts_auto_disable`, `elna_enable`, and DVB `adapter_nr`. `as102_dvb_register()` registers a DVB adapter, demux, dmxdev, AS102 frontend, mutexes, and optionally requests firmware upload. `as102_dvb_unregister()` tears them down. Feed callbacks `as102_dvb_dmx_start_feed()` and `as102_dvb_dmx_stop_feed()` manage `as102_dev_t.streaming`, optional PID filters, and stream start/stop. Frontend operations `as102_set_tune()`, `as102_get_tps()`, `as102_get_status()`, `as102_get_stats()`, and `as102_stream_ctrl()` call AS10x command helpers under the bus adapter lock.

## Control flow and state
Probe in the USB file calls `as102_dvb_register()` after USB buffers are ready. The DVB demux calls start/stop feed for each active PID; the first feed starts USB URBs and possibly firmware streaming, while the last feed stops them. `pid_filtering` changes demux filter count and sends add/delete PID commands. `ts_auto_disable` toggles whether firmware start/stop commands are sent around transport streaming. `elna_enable` controls whether `CONTEXT_LNA` is programmed before turning the demod on.

## Dependencies and integration points
Depends on DVB core demux/dmxdev/frontend APIs, AS102 frontend attach from `as102_fe.h`, AS10x command protocol helpers, and low-level `as102_priv_ops_t` methods. The module is registered via `module_usb_driver(as102_usb_driver)`, with the actual USB driver object defined in `as102_usb_drv.c`.

## Risks and test signals
Critical risks are stream reference-count balance, interruptible mutex failures returning partial setup, firmware upload failures being tolerated for later upload, and PID filter add/delete correctness when hardware filtering is enabled. Test signals include successful adapter/frontend registration, feed start producing TS packets, feed stop dropping streaming to zero, tuning/status/stat queries returning plausible values, and no lock inversion between `sem` and `bus_adap.lock`.
