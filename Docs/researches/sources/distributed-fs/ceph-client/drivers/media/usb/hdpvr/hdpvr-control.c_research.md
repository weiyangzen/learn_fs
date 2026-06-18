<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c

Purpose: firmware-control helper layer for the HD-PVR driver. It translates driver options and V4L2 control values into HD-PVR vendor USB control messages and queries input timing/status information.

Important APIs/types/functions: `hdpvr_config_call()` sends one-byte control settings for video standard/input, bitrate mode, GOP mode, and picture controls. `get_video_info()` reads width, height, and frame rate. `get_input_lines_info()` reads detected line data. `hdpvr_set_bitrate()` writes average/peak bitrate. `hdpvr_set_audio()` configures audio input and, when firmware supports it, AAC/AC3 encoding. `hdpvr_set_options()` pushes the full cached `struct hdpvr_options` block to hardware.

Control flow: callers update `dev->options`, then invoke these helpers under higher-level idle/streaming checks. Each helper locks `dev->usbc_mutex`, writes or reads through `dev->usbc_buf`, issues `usb_control_msg()`, unlocks, and returns a Linux error or zero for normalized success. `hdpvr_set_options()` is used during device initialization and after default option setup.

State and persistence: cached state lives in `dev->options`, `dev->flags`, and the shared `usbc_buf`; hardware state persists in the encoder firmware after successful control requests. The file does not store state outside `struct hdpvr_device`.

Dependencies and integration: depends on USB core, `v4l2_common` logging, and constants/prototypes in `hdpvr.h`. It is called by probe initialization and `hdpvr-video.c` V4L2 controls/ioctls.

Risks: most setters accept short successful USB writes by returning the raw positive length, while some normalize only specific lengths; callers often treat nonzero as failure, so positive partial lengths can be ambiguous. `get_input_lines_info()` suppresses `ret` outside debug and returns data from `usbc_buf` even if the USB transfer failed. `hdpvr_set_options()` ignores individual helper failures and always returns 0.

Test signals: probe with known firmware versions; change all picture controls and bitrate controls through V4L2; switch RCA/SPDIF and AAC/AC3 on AC3-capable and older firmware; query video info with valid/no signal; enable USB/control debug and confirm request values match `hdpvr.h` comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-control.c -->
