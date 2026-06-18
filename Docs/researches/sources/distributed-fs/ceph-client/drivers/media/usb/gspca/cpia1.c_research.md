# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/cpia1.c

Purpose: GSPCA subdriver for Vision CPiA version 1 cameras, including Intel QX3 microscope variants. It implements the CPiA vendor command protocol, camera parameter cache, power-state transitions, stream setup, exposure/flicker management, controls, input button reporting, and packet scanning for `V4L2_PIX_FMT_CPIA1`.

Important APIs and functions: `cpia_usb_transferCmd()` sends low-level vendor control commands with EPIPE retries. `do_command()` and `do_command_extended()` encode command payloads and update `struct cam_params`. Startup paths include `sd_config()`, `sd_init()`, `sd_start()`, and `sd_stopN()`. Device programming helpers cover format, color, exposure, color balance, compression, sensor FPS, flicker, and QX3 lights. Runtime maintenance uses `sd_dq_callback()`, `monitor_exposure()`, and `restart_flicker()`.

Control flow: config resets cached defaults, enters low power, reads firmware/PNP IDs, validates firmware major version, and detects QX3. Start moves through low/high power, clears stream state, reads status/version, calculates ROI and video size from the selected mode, programs all camera subsystems, starts stream capture, and delays compression for the first six frames. Packet scanning recognizes 64-byte CPiA frame headers matching current format/ROI, updates atomic exposure/FPS values, closes completed frames, then appends payload.

State and persistence: `struct sd` stores the complete cached camera parameter model, exposure counters/status, mains frequency, atomics for camera exposure/FPS, and first-frame compression delay. Hardware settings are volatile but saved back into the cache on stop.

Dependencies and integration points: depends on GSPCA core, USB control transfers, V4L2 controls, optional input subsystem for snapshot button reporting, and USB IDs `0553:0002` and `0813:0001`.

Risks and test signals: risks include complex firmware-version quirks, command ordering sensitivity, deadlocks from control transfers during dequeue callbacks, exposure/flicker arithmetic edge cases, frame-boundary validation, and QX3 input/light behavior. Test firmware 1.02 and newer, all four modes, stream start/stop/resume, flicker frequency changes, low-light/high-light transitions, QX3 button and illuminators, malformed headers, and disconnect during control IO.
