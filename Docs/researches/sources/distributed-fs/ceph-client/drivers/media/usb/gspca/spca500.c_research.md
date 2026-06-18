# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca500.c

## Purpose
`spca500.c` supports many SPCA500 based still/video cameras that produce JPEG data. It selects subtype-specific initialization and quantization tables, configures either VGA or SIF mode sets, starts bridge streaming, wraps raw payloads with a generated JPEG header and EOI marker, and exposes brightness, contrast, and saturation controls.

## Important APIs, types, and functions
`struct sd` stores the GSPCA base, a `subtype` from `usb_device_id.driver_info`, and `jpeg_hdr`. Subtype constants cover Agfa, Aiptek, Benq, Creative, D-Link, Gsmart, Intel, Kodak, Logitech, Mustek, Optimedia, PalmPix, and Toptro variants. Register access uses `reg_r`, `reg_w`, `reg_r_12`, and `reg_r_wait`; only the read-wait helpers return status in a way that startup paths check consistently. `write_vector` writes `{request,value,index}` tables. `spca50x_setup_qtable` uploads 64-byte luma/chroma quantization tables.

Device-specific helpers include `spca500_clksmart310_init`, `spca500_setmode`, `spca500_full_reset`, `spca500_synch310`, and `spca500_reinit`. `sd_start` is the main dispatch point for subtype-specific startup sequences. `sd_pkt_scan` parses the SPCA500 packet format and performs JPEG byte stuffing.

## Control flow
At probe, the subtype selects mode coverage: Logitech ClickSmart 310 uses SIF modes, all others use VGA modes. `sd_init` mostly defers work to stream start, except ClickSmart 310 has an early initialization sequence. `sd_start` creates a JPEG 4:1:1 header, sets quality 85, reads a sensor address register for diagnostics, chooses x/y scaling multipliers, then switches on subtype.

ClickSmart 310 gets mode setup, drop-packet enable, quantization table upload, SDRAM init, video-camera mode, interface resynchronization with `usb_set_interface`, visual defaults, and a repeated startup sequence. Creative/Intel and Kodak paths do full reset, enable drop packets, upload different quantization tables, set mode, switch to video mode, and wait for register `0x8000` to report `0x44`. PocketDV/family paths call `spca500_reinit` and use the PocketDV quantization table. Logitech Traveler/ClickSmart 510 use Creative quantization and optional `Clicksmart510_defaults`.

`sd_stopN` disables streaming by writing mode register `0x8003` and video mode `0x8000`, then reads back state. `sd_pkt_scan` treats packets starting with `0xff 0x01` as a new frame marker, emits a previous `LAST_PACKET` with explicit EOI, inserts a fresh JPEG header, skips the 16-byte SPCA500 header, and appends payload. Other packets skip a one-byte packet prefix. Payload data is byte-stuffed by adding `0x00` after every `0xff`.

## State and persistence
Runtime state is subtype and JPEG header only. Device state is all volatile bridge state: quantization tables, mode registers, SDRAM setup, drop-packet enable, and visual defaults. No persistent storage is modified. `reg_w` returns errors but many callers log and keep going, so hardware may be left partially initialized if a mid-sequence write fails.

## Dependencies and integration points
The file integrates with GSPCA and V4L2 via `sd_desc`, `gspca_dev_probe`, `gspca_frame_add`, and V4L2 controls. It depends on `jpeg.h` for JPEG header and quantization quality, the USB core for control transfers and interface switching, and many static tables derived from device traces.

## Risks
The subtype matrix is large and unevenly checked. Several startup paths ignore `reg_r_wait` failures or continue after qtable upload errors. `spca500_synch310` changes alternate interfaces during startup, which can disturb URB setup if GSPCA expectations change. Packet scanning assumes enough bytes for SPCA500 headers and does not guard every short packet. In-place byte stuffing mutates the isochronous buffer. One USB ID maps to Intel Pocket PC Camera with a comment indicating a temporary fix, so behavior may be subtype-specific fragile.

## Test signals
Hardware tests should cover each subtype group, mode selection, successful qtable upload, full reset and wait failure behavior, repeated stream start/stop, ClickSmart 310 interface resync, JPEG validity from packet captures including drop packets and embedded `0xff`, and V4L2 control writes to registers `0x8167`, `0x8168`, and `0x8169`.
