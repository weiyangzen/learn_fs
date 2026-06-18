<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c

Purpose: `etoms.c` supports Etoms ET61x151 USB cameras with either PAS106 or TAS5130CXX sensors. It outputs Bayer `V4L2_PIX_FMT_SBGGR8` frames in SIF or VGA-class modes, configures bridge registers and sensor I2C windows, and includes simple automatic gain based on luma samples read after frames are dequeued.

Important APIs, types, and functions: `struct sd` extends `gspca_dev` with `sensor`, `autogain`, and an autogain countdown. `reg_r()`, `reg_w_val()`, and `reg_w()` wrap vendor control transfers to bridge registers. `i2c_w()` and `i2c_r()` program PAS106 sensor registers through ETOMS I2C staging registers. `Et_init1()` initializes PAS106 paths; `Et_init2()` initializes TAS5130CXX paths. `sd_pkt_scan()` parses isochronous packet headers and emits GSPCA frame packets. `do_autogain()` is wired as `dq_callback`.

Control flow: USB IDs choose the sensor through `driver_info`. Probe sets mode tables and initializes controls. `sd_init()` performs a full bridge/sensor setup and turns video off. `sd_start()` repeats setup, arms autogain, resets the bridge, and enables video. Packets with `seqframe == 0x3f` begin a new frame after closing the prior one; nonzero data packets append after an 8-byte header; zero-length logical payloads discard the frame.

State and persistence: most hardware state is volatile and replayed on init/start. User controls are not cached as V4L2 pointers, except autogain state in `sd->autogain`; brightness, contrast, and saturation writes go directly to bridge/sensor registers when streaming. Autogain persists a countdown and periodically adjusts PAS106 global gain.

Dependencies and integration points: integrates with the GSPCA V4L2 control path, frame assembly, and optional `dq_callback`. It depends on ETOMS-specific register semantics and PAS106 I2C register layouts.

Risks: many USB helpers ignore return values and do not set `usb_err`, so partial hardware failures can be silent. `sd_pkt_scan()` trusts `data[0]` and `data[1]`; the GSPCA core normally avoids zero-length packets, but malformed short packets would be hazardous. Autogain reads bridge luma registers without locking beyond the callback context. Test signals include stable frame boundaries, no discarded packets under normal light, working PAS106 saturation/gain controls, and luma-driven gain convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/etoms.c -->
