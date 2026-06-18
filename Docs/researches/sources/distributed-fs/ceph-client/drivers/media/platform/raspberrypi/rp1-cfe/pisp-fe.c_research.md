# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.c

Purpose: implements the PiSP Front End subdevice used by RP1 CFE for raw stream processing, optional compression, image outputs, and statistics output.

Important APIs/types/functions: `pisp_fe_config_map[]` maps dirty flags to config struct offsets. `pisp_fe_isr()` reports SOF/EOF to the CFE core. `pisp_fe_validate_config()` checks input, output, crop, downscale, and stats safety. `pisp_fe_submit_job()` patches DMA addresses into the config, writes changed hardware config blocks, and queues the FE job. `pisp_fe_start()` and `pisp_fe_stop()` control reset/interrupt/abort. Subdev ops are implemented by `pisp_fe_init_state()`, `pisp_fe_pad_set_fmt()`, and `pisp_fe_link_validate()`.

Control flow: init registers a five-pad processing subdev: stream input, config input, output0, output1, and stats. Format state defaults to 16-bit Bayer stream/output and fixed-size config/stats pads. CFE validates FE config during buffer prepare. When a job is submitted, output and stats buffer DMA addresses are inserted, output line interrupts are computed, status is read as a barrier, required config sections are written based on dirty flags/enables, and `FE_CONTROL_QUEUE` starts the hardware. ISR latches registers, clears interrupt status, traces status, and reports SOF/EOF for source pads.

State and persistence: `pisp_fe_device` holds V4L2 device pointer, MMIO base, hardware revision, in-frame count, pads, and subdev. Per-frame config is supplied by userspace metadata buffers and copied/validated in the CFE core.

Dependencies and integration: depends on PiSP FE UAPI config/statistics headers, CFE format helpers, vb2 DMA addresses, media controller subdevs, debugfs, runtime PM, and CFE tracepoints.

Risks: config writing uses dirty flags from userspace/config buffers, so missing dirty bits can leave stale hardware state; some blocks are forced dirty when enabled to reduce that risk. Validation explicitly guards zero-sized crops/outputs that could lock hardware. `pisp_fe_pad_set_fmt()` has TODOs for propagation and validation. `pisp_fe_submit_job()` mutates the copied config with DMA addresses and clears dirty flags, so callers must not reuse shared userspace memory directly.

Test signals: FE media link validation, config buffer validation for invalid input/output/stats crops, compressed output format negotiation, job submission with output0/output1/stats combinations, FE IRQ trace events, abort/stop behavior, and register debugfs reads.
