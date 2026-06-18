# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.c

Purpose: implements the RP1 CSI-2 receiver/DMA subdevice used by CFE. It configures per-channel packet filtering, DMA buffers, optional remap/compression, interrupt decoding, error tracking, and V4L2 subdev routing/format operations.

Important APIs/types/functions: register helpers `csi2_reg_read/write()`, debugfs show functions, `csi2_isr()`, `csi2_set_buffer()`, `csi2_set_compression()`, `csi2_start_channel()`, `csi2_stop_channel()`, `csi2_open_rx()`, `csi2_close_rx()`, `csi2_pad_set_fmt()`, `csi2_set_routing()`, `csi2_init()`, and `csi2_uninit()`. Module parameter `track_csi2_errors` enables discard/overflow accounting.

Control flow: `csi2_init()` initializes error locks, probes the DPHY, creates debugfs files, initializes pads, finalizes a streams-capable V4L2 subdev, and registers it. The default subdev state creates one active sink-to-source route with `cfe_default_format`. Sink format changes are propagated to the opposite source stream. Source format changes are limited to sink code, 16-bit remap, or compressed remap. Channel start clears old state, programs frame size, VC/DT, mode, pack flags, auto-arm, and FS/FE_ACK IRQs. Buffer programming writes length/stride/high address before low address to trigger hardware double buffering.

State and persistence: state is in `csi2_device`: MMIO base, DPHY data, bus flags, per-channel line counts, subdev/pads, and optional error counters protected by `errors_lock`. Debugfs error reads snapshot and clear counters.

Dependencies and integration: depends on CFE format helpers, DPHY helper, V4L2 subdev routing, media controller, debugfs, runtime PM for register dumps, and vb2 DMA addresses supplied by the CFE core.

Risks: channel stop needs FORCE and two ADDR0 writes, indicating hardware-sensitive sequencing. Wrong VC/DT or routing can silently discard packets. Error tracking is optional and counters are cleared on debugfs read. Source multiplexing is disallowed, so route validation must match userspace expectations. `set_field()` call argument order should be reviewed because the helper parameters are named as field value then mask.

Test signals: subdev routing validation, sink/source format remap attempts, normal/remap/compressed capture, embedded metadata pack-bytes mode, start/stop mid-frame, debugfs register and error counters, and interrupt trace events for FS/FE_ACK.
