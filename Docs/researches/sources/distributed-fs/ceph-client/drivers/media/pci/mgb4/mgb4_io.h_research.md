# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_io.h

- Purpose: Shared video I/O constants and helpers for MGB4 vin/vout queue code.
- Important APIs/types/functions: `MGB4_ERR_*` sentinel addresses, `MGB4_PERIOD`, `struct mgb4_frame_buffer`, `to_frame_buffer`, `has_yuv_and_timeperframe`, `pixel_size`.
- Control flow: Vin/vout use sentinels to detect FPGA frame-queue errors, period macro for timeperframe timers, frame-buffer wrapper for vb2 lists, and pixel-size helper for timing-derived frame periods.
- State and persistence: No state; helpers inspect video status register and timing structures.
- Dependencies and integration points: Depends on V4L2/vb2, math64, and MGB4 register access.
- Risks: Sentinel comparison assumes valid FPGA addresses never overlap high error values. `has_yuv` and `has_timeperframe` are tied to one status bit.
- Test signals: Compile plus streaming tests that force queue empty/full/timeout status and YUV capability detection.
