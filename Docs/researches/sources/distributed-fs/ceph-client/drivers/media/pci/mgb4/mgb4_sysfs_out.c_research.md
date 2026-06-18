# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_out.c

- Purpose: Output-video sysfs interface for MGB4 source routing, display timings, pixel clock, color mapping, polarities, and serializer settings.
- Important APIs/types/functions: Helpers `loopin_cnt()` and `is_busy()`, show/store handlers for output id, video source, color mapping, display width/height, frame rate, sync widths/porches/polarities, FPDL3 output width, and pclk frequency; module-specific attr arrays.
- Control flow: Video-source changes use a global `io_reconfig` bit, check all vin/vout queues for busy state, enable/disable loopback input queues as needed, and update output source/config bits. Timing stores update FPGA registers, many live-safe; dimensions and pclk lock the vdev and reject busy queues. Pclk calls CMT programming and may update FPDL3 serializer double-pixel mode.
- State and persistence: State includes output FPGA registers, `voutdev->freq`, serializer registers, and loopback enable bits. No disk persistence.
- Dependencies and integration points: Used by `mgb4_vout_create()` through module-specific groups; coordinates with vin loopback behavior and CMT/I2C helpers.
- Risks: Cross-device reconfiguration is subtle and intentionally avoids taking all locks simultaneously. Existing streaming blocks source changes, but live timing writes can affect displayed output. Serializer-free on module types without serializer client may depend on zeroed client state.
- Test signals: Test source switching among self-output and both inputs, busy rejection while any queue runs, loopback capture continuity, pclk rounding/double-pixel handling, and all invalid sysfs values.
