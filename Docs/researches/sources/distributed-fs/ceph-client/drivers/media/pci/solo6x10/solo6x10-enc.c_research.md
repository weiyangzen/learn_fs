<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-enc.c

Purpose: low-level capture, OSD, JPEG quality, and MPEG encoder hardware configuration for SOLO6x10 devices.

Important APIs, types, and functions: `solo_enc_init()` calls capture, MPEG, and JPEG configuration and disables per-channel compression initially. `solo_capture_config()` programs capture memory base, bandwidth, dimensions, and clears OSD SDRAM. `solo_osd_print()` renders text with the VGA8x16 font into OSD memory using P2M DMA. `solo_s_jpeg_qp()` and `solo_g_jpeg_qp()` manage per-channel JPEG quality profile registers. `solo_jpeg_config()` sets JPEG QP tables and memory region. `solo_mp4e_config()` programs MPEG encoder block base, endian/attributes, reference bases, and motion registers. `solo_enc_exit()` disables channel scale/compression.

Control flow: init configures capture SDRAM layout and dimensions, clears OSD buffers for every channel, configures MPEG/JPEG engines, initializes QP locks/state, and leaves compression disabled until V4L2 encoder code enables channels. OSD updates write text bitmap data and toggle the channel bit in `SOLO_VE_OSD_CH`.

State and persistence: runtime state includes JPEG QP registers/cache, OSD buffers in `solo_enc_dev`, encoder reference memory layout, and per-channel compression registers. No persistent storage.

Dependencies and integration points: P2M DMA, font subsystem, bit-reversal helper, register definitions, `solo_enc_dev` from V4L2 encoder module, display-provided dimensions, and chip type distinctions.

Risks: OSD requires `FONT_8x16`; missing font returns error. Several P2M DMA return values in setup are ignored, so OSD clearing can partially fail. Chip-specific magic constants affect timing and bandwidth. QP functions silently ignore invalid channels or unsupported 6010 writes.

Test signals: encoder node capture after V4L2 init, JPEG QP controls, OSD text rendering, no P2M errors during OSD clear/update, valid encoded stream timing for 6010 and 6110, and compression disabled on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-enc.c -->
