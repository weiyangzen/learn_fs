# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/nw80x.c

## Purpose
`nw80x.c` is a standalone GSPCA subdriver for DivIO NW800/NW801/NW802 and related ET31x110 webcams. It autodetects bridge generation, selects one of many webcam-specific register scripts, supports a module parameter for webcam type, handles optional auto-exposure/gain, and frames JPGL-like compressed packets.

## Important APIs, Types, And Functions
`struct sd` tracks auto-exposure window size, autogain countdown, exposure high/low counters, bridge generation, and webcam subtype. `enum bridges` and `enum webcams` classify supported hardware; `webcam_chip[]` maps subtypes to bridge generations; `webcam_start[]` selects large register scripts. USB helpers are `reg_w()`, `reg_r()`, `i2c_w()`, `reg_w_buf()`, `nw802_test_reg()`, and `swap_bits()`. Controls use `setgain()`, `setexposure()`, `setautogain()`, `do_autogain()`, and `sd_s_ctrl()`.

## Control Flow
Probe clamps the `webcam` module parameter, marks full bandwidth, initializes autogain off, and detects bridge generation by probing register writability: missing `0x0500` implies NW802, missing `0x109b` implies NW801, otherwise NW800/ET31x110. For `06a5:d800`, GPIO bits refine ET31x110 sensor subtype. The selected subtype must match the detected bridge. Config then chooses CIF or VGA mode tables and available mode count. Init runs any bridge-specific init script. Start runs the base subtype script plus resolution-specific additions for P35u, Kr651us, or Proscope. Packet scan treats an eight-byte `00 00 hh ww ss xx ff ff` header as a new frame and strips it.

## State, Persistence, And Dependencies
State is in `struct sd`, GSPCA controls, and volatile bridge/sensor registers. `reg_w_buf()` interprets script records as big-endian register plus length plus data, with special `I2C0` records routed through bridge I2C. Autogain persists across dequeued frames through `ag_cnt` and `ae_res`. Dependencies include GSPCA, USB vendor control messages, V4L2 auto clusters, and GSPCA exposure/autogain helper algorithms.

## Integration Points
The USB table covers Logitech, DVC, EZCam, Mustek, DivIO, Trust, and AVerMedia-style IDs. Module parameter `webcam` can override subtype selection. `sd_desc` includes `.dq_callback = do_autogain`, so exposure/gain adjustment is tied to frame dequeue rather than packet receipt.

## Risks
The register scripts are large opaque hardware traces; small edits can break specific models. Bridge detection writes test values to hardware registers during probe. Several USB IDs map to many possible webcams, so `webcam` override may be required and mismatches return `-ENODEV`. `sd_pkt_scan()` assumes `len >= 8` before reading header bytes and relies on GSPCA packet sizing. Autogain reads luma registers and divides by `ae_res`; fallback protects zero window size, but wrong AE window registers skew control feedback.

## Test Signals
Probe NW800/NW801/NW802 hardware, subtype overrides, ET31x110 GPIO detection, CIF/VGA mode selection, start scripts for P35u/Kr651us/Proscope at both resolutions, LED-off stop writes, packet header framing with short packets, autogain convergence from `dq_callback`, and USB control error propagation.
