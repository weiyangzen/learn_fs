<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c

Purpose: Linux DVB API bridge for pvrusb2 digital-capable devices. It registers DVB adapters, demux/net devices, attaches frontends/tuners, claims the shared pvrusb2 video stream for DTV, and feeds transport packets into the DVB demux.

Important APIs/types/functions: `pvr2_dvb_create()` allocates and initializes the adapter. `pvr2_dvb_adapter_init()/exit()` register/unregister DVB core objects. `pvr2_dvb_frontend_init()/exit()` attach and register frontends/tuners from device descriptor callbacks. `pvr2_dvb_stream_start()`, `pvr2_dvb_stream_end()`, and `pvr2_dvb_feed_thread()` manage streaming. `pvr2_dvb_start_feed()` and `pvr2_dvb_stop_feed()` are demux feed callbacks. `pvr2_dvb_bus_ctrl()` uses pvrusb2 input limits to acquire/release DTV ownership.

Control flow: setup creates a pvrusb2 channel, registers DVB adapter/demux/dmxdev/net, temporarily limits input to DTV, attaches frontends, registers them, installs `ts_bus_ctrl`, and releases the input limit. When the first demux feed starts, it claims the shared video stream, allocates 32 16KiB buffers, assigns them to pvr2 stream buffers, enables hardware streaming, queues idle buffers, and starts a kernel feed thread. The thread drains ready buffers, pushes payload into `dvb_dmx_swfilter()`, and requeues buffers. Last feed stop tears all streaming state down.

State and persistence: `struct pvr2_dvb_adapter` stores the pvr2 channel, DVB core objects, frontend pointers, dynamically probed I2C clients, feed count, thread pointer, stream-run flag, waitqueue, and buffer storage. State is runtime-only.

Dependencies and integration: depends on DVB core/demux/net APIs, pvrusb2 context/channel/stream/hardware APIs, optional frontend/tuner attach callbacks in device descriptors, kthreads, freezer support, and media I2C module probing.

Risks: several failure paths in `pvr2_dvb_stream_do_start()` return after partial buffer allocation or stream claiming; wrapper cleanup helps but review is needed for every early return. `pvr2_dvb_frontend_init()` returns immediately on no frontend without releasing the DTV input limit in one branch. Dual-frontend setup copies tuner ops/private data from frontend 0 to 1, which depends on frontend implementation expectations. Feed count and stream-run state are protected by `adap->lock`; frontend bus-control callbacks use channel limits separately.

Test signals: digital device probe creates `/dev/dvb/adapter*`; start/stop PID filters repeatedly; stream TS data through demux; freeze/thaw feed thread; disconnect while feeds are active; dual-frontend HVR-1955/1975 attach; fault-inject frontend/tuner attach failures and buffer allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-dvb.c -->
