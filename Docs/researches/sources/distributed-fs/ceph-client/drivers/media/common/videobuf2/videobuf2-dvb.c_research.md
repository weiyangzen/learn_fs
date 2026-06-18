# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-dvb.c

## Purpose
`videobuf2-dvb.c` is helper glue for simple DVB devices that DMA complete transport streams into vb2 buffers and rely on the software demux. It registers DVB adapters/frontends/demux/net devices and uses the vb2 thread-I/O helper to feed completed buffers into `dvb_dmx_swfilter()`.

## Important APIs, Types, and Functions
Exports include `vb2_dvb_register_bus()`, `vb2_dvb_unregister_bus()`, `vb2_dvb_get_frontend()`, `vb2_dvb_find_frontend()`, `vb2_dvb_alloc_frontend()`, and `vb2_dvb_dealloc_frontends()`. Important internal functions are `dvb_fnc()`, `vb2_dvb_start_feed()`, `vb2_dvb_stop_feed()`, `vb2_dvb_register_adapter()`, and `vb2_dvb_register_frontend()`. The code operates on `struct vb2_dvb`, `struct vb2_dvb_frontend`, and `struct vb2_dvb_frontends`.

## Control Flow
Frontend allocation creates list entries and initializes the per-DVB lock. Bus registration requires frontend id 1, registers the adapter, then registers each frontend. Frontend registration calls `dvb_register_frontend()`, initializes a software demux with TS, section, and memory filtering capabilities, registers the demux device, adds hardware and memory frontends, connects the hardware frontend, and registers DVB network support. When a demux feed starts, `nfeeds` is incremented and the vb2 thread starts on the first feed. The thread callback sends each buffer's payload to the software demux. Feed stop decrements `nfeeds` and stops the vb2 thread when the last feed is gone. Unregister/dealloc tears down net, frontend links, dmxdev, demux, frontend registration, frontend attachment, and list nodes.

## State and Persistence
The helper keeps transient adapter/frontend list state plus per-DVB feed counts and vb2 thread state. Nothing is persistent beyond driver binding. `nfeeds` controls when the vb2 thread is active. Frontend list membership and adapter registration determine the lifetime of associated demux and net devices.

## Dependencies and Integration Points
It depends on DVB core APIs (`dvb_register_adapter`, `dvb_register_frontend`, `dvb_dmx_init`, `dvb_dmxdev_init`, `dvb_net_init`), media-controller graph creation when configured, and vb2 core thread I/O. It is used by DVB capture drivers that provide an initialized vb2 queue and frontend structures but want common software-demux plumbing.

## Risks and Edge Cases
Registration has many staged failure paths; each must unwind only resources already initialized. `vb2_dvb_unregister_bus()` first deallocates frontends and then unregisters the adapter, so callers must not use frontend pointers afterward. Feed start requires a connected demux frontend or returns `-EINVAL`. `nfeeds` is protected by `dvb->lock`; imbalance would leave the thread running or stop it too early. Media graph creation failure inside the frontend loop unwinds the whole bus.

## Test Signals
Probe a simple DVB device with one and multiple frontends, start and stop several demux feeds, and confirm the vb2 thread starts once and stops after the final feed. Runtime signals include TS packets reaching `dvb_dmx_swfilter()`, correct `/dev/dvb/adapter*/demux*` and DVR nodes from dmxdev, successful DVB net setup when enabled, clean unregister under active feeds, and no leaked frontend list entries.
