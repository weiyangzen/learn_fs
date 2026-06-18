# sources/distributed-fs/ceph-client/drivers/media/usb/b2c2/flexcop-usb.c

## Purpose
Implements the USB bus layer for B2C2 FlexCop II/IIb/III digital TV devices, connecting common FlexCop DVB logic to USB control transfers, I2C requests, V8 memory access, MAC address readout, and isochronous TS reception.

## Important APIs, types, and functions
`flexcop_usb_readwrite_dw()` reads/writes FlexCop IBI registers via vendor control transfers and PCI/internal address conversion macros. `flexcop_usb_v8_memory_req()` and `flexcop_usb_memory_req()` access V8 memory/flash in page-limited chunks. `flexcop_usb_get_mac_addr()` reads six bytes from flash. `flexcop_usb_i2c_req()` implements firmware-mediated I2C operations. `flexcop_usb_process_frame()` parses 190-byte USB media frames with `0xff` header and embedded TS sync `0x47`, passing packets to `flexcop_pass_dmx_packets()`. `flexcop_usb_transfer_init()` allocates coherent ISO buffers, builds four URBs with four ISO frames each, submits them, then configures SRAM/WAN routing. Probe allocates a `flexcop_device`, installs USB callbacks, initializes common FlexCop, and starts transfer.

## Control flow and state
USB probe sets alternate interface 1, validates endpoint and speed, stores interface data, initializes common FlexCop, and starts continuous ISO URBs. URB completion iterates ISO frames, processes complete payloads, stores trailing partial data in `tmp_buffer`, clears frame statuses, and resubmits. Disconnect kills URBs, frees buffers, exits common FlexCop, clears interface data, and frees state.

## Dependencies and integration points
Depends on USB core, common B2C2 FlexCop APIs, FlexCop I2C adapter abstraction, DVB demux pass-through, SRAM/WAN setup helpers, and module debug configuration.

## Risks and test signals
Risks include continuous URBs with no stream-control gating, partial-frame buffer overflow if unexpected frame sizes exceed `tmp_buffer`, error handling in URB resubmit, and USB endpoint assumptions after altsetting. Test signals include successful register access, I2C tuner/demod communication, MAC address read, demux packets with TS sync, clean disconnect, and no ISO descriptor errors under load.
