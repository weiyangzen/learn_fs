# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/s2250-board.c

Purpose: board-specific V4L2 I2C subdevice for Sensoray 2250/2251. It controls a VPX3226F-like video decoder and TLV320AIC23B-like audio codec through custom GO7007 USB vendor requests rather than reusable generic chip drivers.

Important APIs and functions: `s2250_probe()` creates a dummy audio I2C client, initializes a `v4l2_subdev`, registers brightness/contrast/saturation/hue controls, programs default audio/video registers, and selects composite/line-in defaults. Register helpers include `write_reg()`, `write_reg_fp()`, `read_reg_fp()`, `write_regs()`, and `write_regs_fp()`. Subdev ops implement video routing, standard selection, pad format, audio routing, and status logging.

Control flow: probe initializes audio first, then decoder registers and front-panel registers. `s2250_s_std()` loads NTSC or PAL tables and reselects the active source. `s2250_s_video_routing()` selects composite or S-Video. `s2250_set_fmt()` toggles a decoder bit for smaller active heights. Control writes preserve unrelated register bits where needed.

State and persistence: `struct s2250` caches standard, input, control defaults, last `0x12b` register value, audio input, and the dummy audio client. Hardware register changes persist only until unplug/reset.

Dependencies and integration points: depends on `go7007_usb` private context layout, the USB vendor request protocol from `go7007-usb.c`, Linux I2C dummy clients, and V4L2 subdev/control frameworks. It is instantiated by the GO7007 USB board table entry of type `"s2250"`.

Risks and test signals: risks include duplicated private `go7007_usb` struct assumptions, unchecked positive USB transfer lengths, register-write verification failures, locking interactions with EZ-USB I2C, and incomplete cleanup on probe failures. Test Sensoray probe/remove, PAL/NTSC transitions, composite/S-Video routing, all audio inputs, controls while streaming, and disconnect while vendor request is pending.
