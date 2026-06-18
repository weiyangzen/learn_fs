# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_st6422.c

Purpose: implements support for the integrated ST6422 sensor/bridge variant inside the STV06xx module using direct bridge-register writes rather than external I2C.

Important APIs and functions: callbacks are `st6422_probe`, `st6422_init`, `st6422_init_controls`, `st6422_start`, and `st6422_stop`. Control dispatch `st6422_s_ctrl` writes brightness, contrast, gain, and exposure through `setbrightness`, `setcontrast`, `setgain`, and `setexposure`, then commits settings by writing `0x143f`.

Control flow: probe accepts only `BRIDGE_ST6422` and installs two SGRBG8 modes: 162x120 and 324x240 with extra skipped/ignored lines noted in comments. Init writes a table of bridge registers for disabled capture, brightness/contrast, RGB gain, exposure, timing, and commit. Start writes mode-dependent size register `0x1505` and commits. Stop only logs; common core disables ISO streaming. Packet-level first-line skipping is handled in `stv06xx_pkt_scan` through `sd->to_skip`.

State and persistence: no backend-private allocation is used. Control state is held by V4L2; hardware state is bridge register state reinitialized on probe/resume.

Dependencies and integration points: depends on `stv06xx_st6422.h`, STV06xx bridge helpers, V4L2 controls, and the core packet parser's ST6422 special cases.

Risks: register meanings are largely unknown comments. Stop does not explicitly power down sensor registers. The 324x240 mode reports `sizeimage` for 324x244 while logical height is 240, relying on userspace/GSPCA handling of ignored lines. No bandwidth reduction is known for this backend.

Test signals: probe ST6422 USB IDs, stream both modes, verify first four corrupt lines are skipped, change controls and confirm commit behavior, test stop/start, and inspect frame dimensions consumed by userspace.
