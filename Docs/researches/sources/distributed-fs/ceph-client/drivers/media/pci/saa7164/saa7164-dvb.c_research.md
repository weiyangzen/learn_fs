<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-dvb.c

Purpose: DVB frontend/demux support for SAA7164 transport-stream ports. It attaches demodulators and tuners for supported Hauppauge boards, allocates TS DMA buffers, registers DVB adapters, and starts or stops firmware DMA based on demux feed usage.

Important APIs, types, and functions: `saa7164_dvb_register()` selects frontend/tuner attach logic by board and port, then calls internal `dvb_register()`. `dvb_register()` allocates hardware buffers, registers `dvb_adapter`, frontend, demux, dmxdev, frontends, and `dvb_net`. `saa7164_dvb_start_feed()` and `saa7164_dvb_stop_feed()` manage `dvb->feeding` and call port state transitions. `saa7164_dvb_unregister()` tears down buffers, I2C clients, DVB net, demux, frontend, and adapter.

Control flow: registration builds frontend dependencies first; if successful, it registers DVB core plumbing. The first feed configures buffers and transitions firmware through acquire, pause, run. The last feed transitions pause, acquire, stop and marks buffers free. IRQ delivery is handled in core by `dvb_dmx_swfilter_packets()`.

State and persistence: state lives in `port->dvb`, `port->dmaqueue`, frontend pointers, and I2C client pointers. Feeding count is mutex protected. No persistent storage is modified.

Dependencies and integration points: integrates with tda10048, tda18271, s5h1411, lgdt3306a, si2168, si2157, DVB demux/net, SAA7164 I2C translation, firmware state API, and buffer API.

Risks: attach failure paths for some client-created demods/tuners rely on manual `module_put()` and unregister ordering. `saa7164_dvb_acquire_port()` accepts `SAA_ERR_ALREADY_STOPPED` for acquire/pause states, which may mask unexpected firmware state. Buffer allocation failures before adapter registration leave cleanup to outer unregister only if called.

Test signals: successful frontend registration per board variant, tuning/lock, demux feed start/stop without leaked DMA, `dvb_net` creation, I2C client module refcounts balanced on unload, and TS continuity under sustained capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-dvb.c -->
