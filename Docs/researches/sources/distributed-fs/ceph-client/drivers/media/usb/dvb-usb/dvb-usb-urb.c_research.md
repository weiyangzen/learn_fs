# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-urb.c

Purpose: generic USB transfer and transport-stream URB glue for DVB USB devices. It provides bulk command read/write helpers and initializes per-frontend data streams that feed DVB demux software filters.

Important APIs/functions: exported `dvb_usb_generic_rw()` and `dvb_usb_generic_write()` implement control transfers over a configured bulk endpoint. `dvb_usb_adapter_stream_init()` and `dvb_usb_adapter_stream_exit()` initialize and release `usb_data_stream` instances. Completion callbacks select `dvb_dmx_swfilter()`, `_204()`, or `_raw()`.

Control flow: command callers pass a write buffer and optional read buffer. The helper validates endpoint/property state, locks `usb_mutex`, sends a bulk message, optionally sleeps, receives from either response endpoint or the same endpoint, dumps debug data, and unlocks. Stream init loops over frontend properties, sets USB device, completion callback based on TS flags, user private pointer, and calls `usb_urb_init()`. Data completion filters packets only when `feedcount > 0` and DVB adapter state is active.

State and persistence: per-FE `usb_data_stream` holds URBs, endpoint properties, callback, and `user_priv`. Device `usb_mutex` serializes generic command traffic. Hardware state is ongoing bulk URB submission owned by lower `usb_urb_*()` helpers.

Dependencies and integration: depends on DVB USB common state, USB bulk APIs, lower USB data-stream helpers, and DVB demux software filters.

Risks: short writes return `-1` rather than a specific errno. Read-side short transfers are not explicitly converted to an error. All generic command users share one mutex, so long firmware delays can serialize unrelated operations. Completion callbacks depend on `feedcount` being consistent with URB submit/kill.

Test signals: generic command timeout and short-transfer paths, separate response endpoint devices, TS 188-byte/204-byte/raw payload filtering, stream init/exit for multi-frontend adapters, feed start/stop URB submission, and disconnect while URBs are active.
