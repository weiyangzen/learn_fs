
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/dvb-ttusb-budget.c

## Purpose
`dvb-ttusb-budget.c` is the DVB driver for Technotrend/Hauppauge Nova-USB budget devices without an onboard MPEG decoder. It boots the device DSP, exposes a DVB adapter/demux/net interface, implements an I2C bridge to frontends/tuners, parses the device mux stream from isochronous USB packets, and attaches multiple possible DVB-S/T/C frontend combinations by USB product ID.

## Important APIs, Types, and Functions
The central type is `struct ttusb`, whose first field is `struct dvb_demux` to support casts from demux feed callbacks. Important functions include `ttusb_cmd()`, `ttusb_i2c_msg()`, `master_xfer()`, `ttusb_boot_dsp()`, `ttusb_init_controller()`, `ttusb_set_channel()`, `ttusb_del_channel()`, `ttusb_process_frame()`, `ttusb_process_muxpack()`, `ttusb_iso_irq()`, `ttusb_start_iso_xfer()`, `ttusb_stop_iso_xfer()`, `ttusb_start_feed()`, `ttusb_stop_feed()`, `frontend_init()`, `ttusb_probe()`, and `ttusb_disconnect()`. The driver registers USB IDs `0x0b48:0x1003`, `0x1004`, and `0x1005`.

## Control Flow
Probe binds interface 1, allocates state, sets USB interface altsetting, allocates isochronous URBs, initializes the controller by reset commands, DSP firmware upload (`ttusb-budget/dspbootcode.bin`), I2C bitrate setup, and version queries, then registers a DVB adapter, I2C adapter, demux, dmxdev, and DVB net. `frontend_init()` chooses frontend attachments by product ID and fallback probing order. Starting the first demux feed sends a device channel command for the PID and starts isochronous transfers. URB completions feed packets to `ttusb_process_frame()`, a state machine that searches for three `0xaa` sync bytes, reads muxpack count, accumulates muxpack payloads, validates checksum/counter continuity, and forwards TS packets to `dvb_dmx_swfilter_packets()`. Stopping the final feed deletes the channel and kills URBs. Disconnect stops streaming and releases DVB, frontend, I2C, URB, and adapter resources.

## State and Persistence
Runtime state includes USB pipe numbers, transaction counter, frontend pointer, I2C locks, demux/feed counts, active isochronous URBs, mux parser state, continuity counter, LNB voltage/tone state, firmware/controller revision, and last command result buffer. Firmware is persisted externally as `ttusb-budget/dspbootcode.bin`; other state is volatile.

## Dependencies and Integration Points
The driver depends on USB bulk/isochronous APIs, Linux firmware loader, I2C core, DVB adapter/demux/dmxdev/net, and numerous DVB frontend modules (`cx22700`, `tda1004x`, `ves1820`, `tda8083`, `stv0299`, `stv0297`, `lnbp21`). It exposes an I2C adapter used by attached demods and tuner callbacks and uses DVB feed callbacks for PID-based streaming.

## Risks and Edge Cases
The command helper serializes USB control traffic but uses fixed packet/result sizes, so unexpected firmware responses can desynchronize higher-level commands. The mux parser has hard `BUG_ON()` for pointer overflow and logs continuity/checksum errors; malformed USB data can cause packet loss or warnings. Hardware section filtering is disabled and incomplete. Frontend attach depends on product ID and probing order; missing modules or different board revisions leave no frontend. Isochronous streaming starts only when the first feed starts, so feed-count accounting must stay balanced.

## Test Signals
Test DSP firmware request/upload, STC/DSP version logging, frontend attach for product IDs `1003/1004/1005`, I2C transfer through each tuner path, DVB scan/lock for DVB-S/T/C variants, LNB voltage/tone for satellite boards, demux start/stop feed balance, TS packet continuity under load, DVB net traffic, disconnect while feeds are active, and operation with frontend modules absent.
