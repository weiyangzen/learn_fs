# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-dvb.c

Purpose: DVB-core integration layer for the DVB USB library. It registers DVB adapters, demux devices, DVB net, media-controller devices, frontend instances, and feed callbacks that start/stop USB streaming.

Important APIs/functions: `dvb_usb_adapter_dvb_init()`/`exit()` set up and tear down the DVB adapter and demux. `dvb_usb_adapter_frontend_init()`/`exit()` attach, register, wrap, and detach frontends. `dvb_usb_ctrl_feed()` is the demux feed state machine. `dvb_usb_fe_wakeup()` and `dvb_usb_fe_sleep()` wrap frontend init/sleep with device power and active-FE selection.

Control flow: adapter init registers `dvb_adapter`, optionally creates a media device, reads MAC address, initializes `dvb_demux`, `dmxdev`, and DVB net. Feed start/stop adjusts `feedcount`, kills URBs and disables streaming when the last feed stops, programs PID filters for each feed, enables PID parser and streaming when the first feed starts, and submits URBs. Frontend init calls board `frontend_attach`, wraps frontend ops, registers each frontend, attaches tuners, creates a media graph, and registers the media device.

State and persistence: persistent adapter state includes `dvb_adap`, `demux`, `dmxdev`, `dvb_net`, `active_fe`, `feedcount`, per-FE stream/filter flags, and saved frontend sleep/init callbacks. Hardware state includes device power, streaming enable, PID parser/filter entries, and active frontend routing.

Dependencies and integration: depends on DVB core, demux/net/frontend APIs, optional media controller, and device callbacks supplied in `dvb_usb_adapter_properties`.

Risks: `feedcount` is updated before later errors, so failed streaming/PID parser calls can leave counts inconsistent. Stop-feed subtracts without explicit underflow protection. Frontend attach failures after `i > 0` can leave earlier FEs alive by design. Active-FE selection assumes frontend IDs match initialized array indexes.

Test signals: DVB adapter registration, `dvbv5-scan`/zap feed start-stop cycles, multi-FE devices with exclusive lock, PID filtering on/off, media-controller graph creation, MAC address reading, and disconnect while feeds are active.
