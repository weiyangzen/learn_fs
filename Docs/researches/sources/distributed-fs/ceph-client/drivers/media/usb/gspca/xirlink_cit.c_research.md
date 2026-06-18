# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/xirlink_cit.c

## Purpose
`xirlink_cit.c` is a GSPCA subdriver for Xirlink C-It/IBM PC Camera/IBM NetCamera/Veo Stingray USB cameras. It supports several hardware revisions named `CIT_MODEL0` through `CIT_MODEL4`, plus an `CIT_IBM_NETCAM_PRO` variant selected by module parameter. The driver exposes model-specific V4L2 modes and controls, programs large model-specific register sequences, performs custom isochronous packet-size negotiation for one path, parses proprietary frame-start markers, and reports camera-button input events for supported models.

## Important APIs, Types, and Data
`struct sd` embeds `struct gspca_dev` and stores the optional lighting control pointer, model enum, input index, last button state, whether control changes require stream restart, and SOF parser state (`sof_read`, `sof_len`).

Module parameters:

- `ibm_netcam_pro`: treats model 3 devices as IBM NetCamera Pro and selects a different init/start path.
- `rca_input`: programs model 3 style devices for RCA input using `rca_initdata[]` instead of the CCD sensor.

Mode tables describe the supported frame formats:

- `cif_yuv_mode`: 176x144 and 352x288 `V4L2_PIX_FMT_CIT_YYVYUY`.
- `vga_yuv_mode`: 160x120, 320x240, and 640x480 `CIT_YYVYUY`.
- `model0_mode`: 160x120, 176x144, and 320x240 `CIT_YYVYUY`.
- `model2_mode`: 160x120 and 176x144 `CIT_YYVYUY`, plus 320x240 and 352x288 raw Bayer `SGRBG8`.

Low-level USB helpers are `cit_write_reg()` and `cit_read_reg()`. Model command helpers such as `cit_Packet_Format1()`, `cit_PacketFormat2()`, `cit_model2_Packet1()`, `cit_model3_Packet1()`, and `cit_model4_Packet1()` encode repeated vendor-register write protocols used by different hardware generations.

GSPCA descriptors are split between `sd_desc` and `sd_desc_isoc_nego`. The latter installs `.isoc_init` and `.isoc_nego` for the IBM NetCamera Pro path.

## Control Flow
`sd_probe()` validates that the matched USB device is being probed on the expected interface number. Model 0/1 require interface 2; model 2/3/4 require interface 0. If `ibm_netcam_pro` is set for model 3, it selects `sd_desc_isoc_nego`; otherwise it uses `sd_desc`.

`sd_config()` stores the model from `driver_info`, remaps model 3 to `CIT_IBM_NETCAM_PRO` when requested, selects the mode table, sets `sof_len` defaults, marks some models as needing stop/restart around control changes, and sets V4L2 input flags for the NetCamera Pro.

`sd_init()` performs only limited work. Model 0 calls `cit_init_model0()` then `sd_stop0()`. NetCamera Pro calls its long init sequence then stops. Other models defer initialization to stream start.

At stream start, `sd_start()` reads the active endpoint max packet size, dispatches to one of the model-specific `cit_start_*()` functions, programs registers `0x0106`/`0x0107` with the packet size, and calls `cit_restart_stream()`. Each `cit_start_*()` function writes a long hardware sequence chosen by model and resolution. Model 0 and 1 compute a clock divider from available isochronous bandwidth via `cit_get_clock_div()`. Model 2 and 4 set `sof_len` per resolution and use fixed or empirically derived timing values. Model 3 has separate CCD and optional RCA-input setup. NetCamera Pro combines model 3 packet helpers with its own init and bandwidth-based clock divider.

`sd_isoc_init()` and `sd_isoc_nego()` implement a custom negotiation strategy for the descriptor variant. They directly modify the cached endpoint `wMaxPacketSize`, start at a resolution-dependent maximum, then reduce by 100 bytes down to a resolution-dependent minimum while calling `usb_set_interface()` on altsetting 1.

`sd_stopN()` writes register `0x010c` to stop streaming. `sd_stop0()` performs model-specific LED-off, sensor idle, control ungrab, and hardware-stop sequences. It also releases a pressed camera button in the input subsystem to avoid a stuck key state.

Frame parsing uses `cit_find_sof()`. Models 0/1/3/NetCamera Pro search for a 4-byte marker beginning `00 ff` plus resolution/model-dependent bytes, then skip `sof_len`. Models 2/4 use a shorter `00 ff` marker and a model/resolution-specific `sof_len`. `sd_pkt_scan()` closes the previous frame with bytes before the marker, starts a new frame, then appends remaining data as `INTER_PACKET`.

If input support is enabled, `cit_check_button()` runs as a dequeue callback for model 3 and NetCamera Pro. It reads register `0x0113`, maps zero to pressed, acknowledges press events by writing `0x01` to the same register, and emits `KEY_CAMERA` transitions.

## State and Persistence
Per-device state in `struct sd` controls the active model path, whether controls stop/restart streaming, current SOF parser progress across packet boundaries, expected SOF length, and last input-button state. Model 2 grabs the lighting/backlight compensation control while streaming because the value cannot safely change on the fly, and releases it in `sd_stop0()`.

There is no persistent storage. Module parameters affect behavior at load/probe time and can materially change mode tables, descriptor callbacks, and hardware initialization.

The code sets `gspca_dev->usb_err = 0` in `sd_s_ctrl()` and returns it, but most Xirlink register writes do not update `usb_err`, so many control and init failures are visible only in logs.

## Dependencies and Integration Points
The driver depends on GSPCA for USB lifecycle, isochronous URB management, V4L2 controls, frame assembly, optional input-device registration, suspend/resume, and disconnect. It depends on Linux USB control transfers for all camera programming. It uses `V4L2_PIX_FMT_CIT_YYVYUY`, a proprietary packed YUV format, and raw Bayer for some model 2/4 modes.

The USB ID table distinguishes revisions using `USB_DEVICE_VER()` and `bcdDevice`, not only vendor/product. Correct behavior depends on matching the hardware revision to the right model path.

The isochronous negotiation path mutates USB descriptor cache fields, which is an unusual integration point and should be treated carefully around USB core changes.

## Risks and Edge Cases
`cit_write_reg()` logs errors but always returns 0 and does not set `gspca_dev->usb_err`. Model start functions also ignore most return values. A device can fail to program while the GSPCA core sees a successful start.

The file contains many magic register sequences inherited from old drivers and Windows traces. Several comments are marked `FIXME` or `TESTME`, including model 3 versus NetCamera Pro autodetection, RCA input using a module parameter instead of V4L2 input selection, SOF signature confidence for model 2/4, and clock-divider selection for model 3.

`cit_find_sof()` maintains parser state across packets. False SOF markers or corrupted packets can prematurely close frames. The short model 2/4 marker is explicitly called out as needing a longer signature.

Control changes for model 3 and NetCamera Pro stop and restart streaming, so controls are not side-effect-free and can disturb frame delivery. Model 2 lighting is grabbed while streaming because changing it live is unsafe.

The module parameter `ibm_netcam_pro` is not autodetected and changes both initialization and isochronous negotiation. Wrong parameter use can make a model 3 camera fail or expose the wrong modes.

`sd_isoc_init()` assumes `actconfig->intf_cache[0]` and altsetting 1. It checks counts but still directly edits descriptor state, so tests need real hardware and multiple host controllers.

## Test Signals
Probe tests should verify the correct interface number is accepted for each model and wrong interfaces return `-ENODEV`. Start tests should show successful endpoint packet-size reads, correct mode table exposure by model, LED behavior, and stable frames in every resolution.

Packet tests should validate SOF detection across packet boundaries, false marker resistance, model 2/4 `sof_len` differences, and frame size consistency for `CIT_YYVYUY` and Bayer modes. Control tests should cover brightness, contrast, hue, sharpness, hflip, lighting, stop/restart-on-control-change behavior, lighting control grab/release, and NetCamera Pro parameter behavior. Input tests should verify `KEY_CAMERA` press/release and forced release on stop.
