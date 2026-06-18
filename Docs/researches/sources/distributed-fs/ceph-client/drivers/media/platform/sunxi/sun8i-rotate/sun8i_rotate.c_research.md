# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_rotate.c

Purpose: implements the Allwinner DE2 rotation unit as a V4L2 memory-to-memory device with format negotiation, rotation/flip controls, DMA address programming, IRQ completion, and runtime PM.

Important APIs and functions: module entry is `module_platform_driver(rotate_driver)`. Key functions include `rotate_device_run`, `rotate_irq`, format ioctls, `rotate_s_ctrl`, vb2 queue callbacks, `rotate_open`, `rotate_release`, platform probe/remove, and runtime resume/suspend.

Control flow: open allocates a per-file context, sets default ARGB32 source and matching capture format, creates an M2M context, installs hflip/vflip/rotate controls, and attaches the control handler. Output format changes validate and align dimensions and then recompute capture format; rotation control changes also recompute capture geometry and reject changes when the capture queue is busy. Streaming the output queue resumes runtime PM. Each M2M job programs global control with mode, flips, rotation, and burst length; programs input format, size, pitches, and plane addresses; programs output size, pitches, and addresses; enables finish IRQ; and starts the hardware. IRQ completion clears the finish flag, marks source and destination buffers done, and finishes the job.

State and persistence: per-context state includes source/destination formats, controls, and current transform values. Device state includes V4L2/video/M2M objects, MMIO base, bus/mod clocks, reset, and mutex. Hardware state is per job and reset/powered by runtime PM.

Dependencies and integration points: depends on V4L2 mem2mem, V4L2 controls/events, vb2 DMA-contig, format helpers from `sun8i_formats.c`, platform IRQ/MMIO, clocks, reset, and runtime PM. Compatible is `allwinner,sun8i-a83t-de2-rotate`.

Risks: `rotate_device_run` returns early on unexpected missing formats without completing the M2M job, though format validation should prevent this. High DMA address registers are zeroed. Capture format for YUV inputs is forced to YUV420, so userspace must handle format conversion semantics. Runtime PM is tied to output queue streaming only. `rotate_open` error cleanup after `rotate_setup_ctrls` failure frees the context without releasing a successfully initialized M2M context.

Test signals: v4l2-compliance for M2M and controls, rotation at 0/90/180/270, hflip/vflip combinations, RGB and YUV format jobs, capture geometry changes with busy queues, streamoff cleanup, IRQ completion, and runtime PM suspend/resume.
