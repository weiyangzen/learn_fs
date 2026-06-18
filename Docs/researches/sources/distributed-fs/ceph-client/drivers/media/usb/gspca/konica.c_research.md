<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c

Purpose: `konica.c` supports Konica-chipset USB webcams such as Intel YC76. It is notable for using two isochronous endpoints in tandem: one data endpoint and one status endpoint used to frame and filter data packets.

Important APIs, types, and functions: `struct sd` stores the last data URB and snapshot-button state. `reg_w()` and `reg_r()` perform vendor register access. `sd_start()` manually creates four URBs because `cam.no_urb_create` is set. `sd_isoc_irq()` pairs data/status URBs by `start_frame`, interprets one-byte status packets, reports optional input events, and emits frame data. `sd_s_ctrl()` writes brightness, contrast, saturation, white balance, and sharpness, briefly stopping the stream around each register write.

Control flow: probe configures three `V4L2_PIX_FMT_KONICA420` modes and disables core URB creation. Init waits roughly six seconds for firmware boot and polls register `0x10` for readiness. Start writes mode value from `.priv`, turns streaming on, allocates alternating endpoint URBs, and lets the GSPCA core submit them. Status bytes with bit 7 start a new frame; bit 0 drops padding data; bit 6 reports the camera button.

State and persistence: `last_data_urb` pairs asynchronous completions. `snapshot_pressed` prevents duplicate input events and is cleared on stop. Control values are not cached beyond V4L2 core state.

Dependencies and integration points: depends on GSPCA custom URB support (`no_urb_create`), Linux input when enabled, and fixed endpoint addresses `0x81/0x82`.

Risks: synchronization assumes status URB arrives after its matching data URB; lost ordering discards/resubmits. Manual URB allocation must match core destruction expectations. Test signals include paired URB start frames, button press/release events, no stuck pressed state after stop, and control writes without stream loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/konica.c -->
