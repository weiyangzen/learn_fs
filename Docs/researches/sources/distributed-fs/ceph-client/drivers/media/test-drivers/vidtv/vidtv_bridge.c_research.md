# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.c

Purpose: platform bridge for vidtv. It registers a virtual DVB adapter, creates virtual I2C tuner/demod clients, wires DVB demux/dmxdev/frontends, and starts/stops the MPEG-TS mux when demux feeds are active.

Important APIs/types/functions: module parameters control lock-loss probabilities, tune/power delays, valid DVB-T/C/S frequencies, frequency tolerance, SI/PCR periods, mux rate, PCR PID, mux buffer size, and adapter number. Major functions include `vidtv_start_streaming()`, `vidtv_stop_streaming()`, `vidtv_start_feed()`, `vidtv_stop_feed()`, `vidtv_bridge_i2c_register_adap()`, `vidtv_bridge_probe_demod()`, `vidtv_bridge_probe_tuner()`, `vidtv_bridge_dvb_init()`, `vidtv_bridge_probe()`, and `vidtv_bridge_remove()`. `vidtv_bridge_on_new_pkts_avail()` injects packets into `dvb_dmx_swfilter_packets()` when demod lock is present.

Control flow: module init registers a platform device and driver. Probe allocates `struct vidtv_dvb`, initializes optional media controller data, registers a virtual I2C adapter and DVB adapter, probes demod/tuner modules using `dvb_module_probe()`, registers frontends, initializes DVB demux and demux device, connects demux frontends, and registers media device if configured. Starting the first demux feed grabs `feed_lock`, increments `nfeeds`, creates a mux with configured timing/network IDs, starts its work thread, and returns the active feed count. Stopping the last feed stops and destroys the mux. Packet callbacks drop TS packets if the demod reports loss of full lock.

State and persistence: `struct vidtv_dvb` holds platform device, frontend/client pointers, DVB adapter/demux/dmxdev, feed count, feed lock, streaming flag, mux pointer, and optional media device. Runtime state is reset on module remove; no persistence exists.

Dependencies and integration points: integrates with platform driver core, I2C adapter/client model, DVB adapter/frontend/demux/dmxdev APIs, media controller, virtual tuner/demod modules, and `vidtv_mux`. Satellite frequency module parameters are translated from Ku-band kHz to tuner IF Hz before tuner probe.

Risks: `NUM_FE` is fixed at one. Virtual I2C `master_xfer()` is a stub, acceptable for platform-data probing but not real bus IO. `vidtv_stop_feed()` decrements `nfeeds` without an explicit underflow guard. Mux buffer sizing is derived from mux rate/sleep interval and clamped; too small a module parameter may still stress overflow guards in TS writers. Cleanup paths must keep tuner/demod/frontend unregister order correct.

Test signals: `modprobe dvb_vidtv_bridge`, DVB adapter/frontend/demux node creation, tuning to configured frequencies, starting/stopping demux feeds, packet flow through `dvb_dmx_swfilter_packets()`, lock-loss simulation by module params, and media-controller graph registration when enabled.
