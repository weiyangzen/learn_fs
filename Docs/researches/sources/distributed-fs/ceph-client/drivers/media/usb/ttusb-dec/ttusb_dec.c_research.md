
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-dec/ttusb_dec.c

## Purpose
`ttusb_dec.c` supports Technotrend/Hauppauge DEC2000-t, DEC2540-t, and DEC3000-s USB DVB boxes with onboard firmware and MPEG/PVA transport behavior. It handles firmware boot, command/result bulk protocol, isochronous receive parsing, DVB demux/net registration, optional IR remote input, and section/PVA stream conversion to DVB feed callbacks.

## Important APIs, Types, and Functions
Central state is `struct ttusb_dec`, containing model metadata, DVB adapter/demux/dmxdev/net/frontend, PID selections, USB pipes, ISO/IRQ URBs, packet parser state, PES-to-TS converters, frame bottom-half work, filter-info list, input device, and active flag. Important functions include `ttusb_dec_send_command()`, `ttusb_dec_get_stb_state()`, `ttusb_dec_boot_dsp()`, `ttusb_dec_init_stb()`, `ttusb_dec_init_usb()`, `ttusb_dec_init_dvb()`, `ttusb_dec_start_feed()`, `ttusb_dec_stop_feed()`, `ttusb_dec_process_urb()`, `ttusb_dec_process_urb_frame_list()`, `ttusb_dec_process_urb_frame()`, `ttusb_dec_process_packet()`, `ttusb_dec_process_pva()`, `ttusb_dec_process_filter()`, `ttusb_init_rc()`, `ttusb_dec_probe()`, and `ttusb_dec_disconnect()`.

## Control Flow
Probe allocates state, selects model/firmware name by USB product ID, initializes USB pipes and URBs, queries firmware state, boots DSP firmware if needed after CRC32 and CRC16 validation, initializes DVB adapter/demux/frontend, attaches DVB-T or DVB-S frontend wrappers, initializes parser/filter/workqueue state, switches to the input streaming interface, and optionally starts the interrupt URB for remote control. Commands are serialized with `usb_mutex`, sent as `0xaa` transaction packets on the command pipe, and answered on the result pipe. Isochronous URB completions copy frame data into `struct urb_frame` allocations and queue bottom-half work. The work parser byte-swaps frames, searches for sync, determines PVA/section/empty packets, validates checksum and packet IDs, then forwards PVA video/audio through PES-to-TS conversion or section packets to registered filters. DVB feed start programs PIDs or section filters with device commands, increments stream counts, and starts ISO transfers; stop removes filters/PIDs and stops ISO when counts reach zero.

## State and Persistence
Persistent external artifacts are model firmware files `dvb-ttusb-dec-2000t.fw`, `dvb-ttusb-dec-2540t.fw`, and `dvb-ttusb-dec-3000s.fw`. Runtime state includes USB interface mode, transaction count, iso stream count, parser state, next packet ID, PVA/filter stream counts, selected PID array, section filter mapping list, pending bottom-half frame list, optional remote input state, and whether firmware supports playback. All runtime state is freed on disconnect.

## Dependencies and Integration Points
The file depends on USB bulk/iso/int APIs, firmware loader, CRC32, input subsystem, workqueues, DVB adapter/demux/dmxdev/net APIs, and local frontend attach helpers from `ttusbdecfe.h`. It registers USB IDs `0x0b48:0x1006`, `0x1008`, and `0x1009`.

## Risks and Edge Cases
Firmware validation has multiple failure modes: unavailable file, too-small file, CRC mismatch, and command failure. Isochronous completion allocates frame wrappers with `GFP_ATOMIC`; allocation failure silently drops frames. Parser state handles odd section payloads, byte swapping, packet loss warnings, and PVA postbyte stitching; malformed streams can produce drops or warnings. `ttusb_dec_stop_iso_xfer()` decrements stream count without an explicit underflow guard. Remote-control key repeat is simplified as immediate down/up events. Disconnect cleanup only runs full teardown when `active` is set, so failures before that rely on probe error paths.

## Test Signals
Test all three model IDs, firmware boot and already-booted firmware paths, CRC failure handling, DVB-T and DVB-S frontend attach, section filters and audio/video PVA feeds, `output_pva` behavior, stream count balance under multiple feeds, packet-loss/checksum logging with corrupted data, remote control with `enable_rc=1`, suspend-like interface switches, and disconnect during queued bottom-half work and active ISO transfers.
