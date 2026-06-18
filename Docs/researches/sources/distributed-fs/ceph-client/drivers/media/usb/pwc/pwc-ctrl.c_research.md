## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-ctrl.c

### Purpose
`pwc-ctrl.c` sends USB vendor control messages to Philips/OEM webcams, selects video modes, initializes decompressor state for compressed modes, enumerates supported frame rates, and controls power, LEDs, and sensor queries.

### Important APIs, Types, And Functions
Important public functions are `pwc_set_video_mode()`, `pwc_get_fps()`, `pwc_get_u8_ctrl()`, `pwc_set_u8_ctrl()`, `pwc_get_s8_ctrl()`, `pwc_get_u16_ctrl()`, `pwc_set_u16_ctrl()`, `pwc_button_ctrl()`, `pwc_camera_power()`, `pwc_set_leds()`, and debug-only `pwc_get_cmos_sensor()`. Internal mode functions are `set_video_mode_Nala()`, `set_video_mode_Timon()`, and `set_video_mode_Kiara()`. The file owns Nala mode tables by including `pwc-nala.h` and consumes Timon/Kiara tables.

### Control Flow
Mode selection starts in `pwc_set_video_mode()`, which maps requested dimensions to a PWC size and dispatches by chipset family. Nala clamps frame rate to a table-supported value and uses a three-byte command. Timon and Kiara clamp to 5-30 fps, progressively raise compression until an available alternate setting is found, and use table commands of 13 or 12 bytes. When requested and compressed YUV output is selected, the relevant decompressor initializer runs. The chosen mode updates `pixfmt`, `vframes`, `valternate`, dimensions, `vbandlength`, `frame_size`, and `frame_total_size`.

### State, Persistence, And Dependencies
State is written into `struct pwc_device` and the camera over USB control endpoint zero. `cmd_buf` records the last video command for raw-frame export. `ctrl_buf` is reused as the transfer buffer. Dependencies include USB control messaging, chipset macros from `pwc.h`, mode tables, and decompressor initializers.

### Integration Points
`pwc-if.c` calls `pwc_set_video_mode()` during probe and stream start, retrying with higher compression on bandwidth errors. `pwc-v4l.c` calls control helpers from V4L2 control callbacks. LED and power helpers are used during stream start/stop and probe shutdown.

### Risks
Bandwidth retry depends on the caller preserving and increasing the compression argument. The Kiara endpoint command special case sends to endpoint 4 even though video is endpoint 5. Control helpers assume `ctrl_buf` is allocated and serialize through higher-level locks. Nala compressed YUV calls `pwc_dec1_init()`, but the actual codec1 decompressor path is not implemented.

### Test Signals
Test mode negotiation across Nala, Timon, and Kiara devices, requested frame-rate clamping, compression fallback on `-ENOSPC`, LED range clamping, power-save eligibility by device type/release, control-message error propagation, and raw-frame command metadata.
