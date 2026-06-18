<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-disp.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-disp.c

Purpose: low-level video input/output, display, and motion-detection memory setup for SOLO6x10 devices.

Important APIs, types, and functions: `solo_disp_init()` determines NTSC/PAL size/fps, calls input, motion, and output setup, and enables windows. `solo_vin_config()` programs video input timing, format, playback ranges, and channel enable behavior. `solo_vout_config()` programs output timing, colors, display base, cursor, and channel enables. `solo_motion_config()` clears motion flag/working areas and sets default thresholds. `solo_set_motion_threshold()` and `solo_set_motion_block()` update motion threshold tables via P2M DMA. `solo_disp_exit()` disables display/window registers.

Control flow: initialization writes timing and SDRAM layout registers, clears motion memory, writes default thresholds, configures display output, then enables per-channel windows. Exit clears display, zoom, freeze, window, border, and rectangle registers.

State and persistence: updates runtime fields `video_hsize`, `video_vsize`, `fps`, input/output starts, and motion memory in device SDRAM. No persistent storage.

Dependencies and integration points: SOLO register definitions, P2M DMA helper, video type selected by TW28/V4L2 code, and encoder/display V4L2 modules that use dimensions and motion state.

Risks: `solo_set_motion_threshold()` checks `ch > nr_chans`, allowing `ch == nr_chans`, likely one past valid channels. Motion memory layout includes a documented mystery block copied from reference code. P2M DMA failures during motion config are mostly ignored in init.

Test signals: display output timing for NTSC/PAL, channel window enablement, motion threshold control behavior, P2M DMA error absence, and clean register shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-disp.c -->
