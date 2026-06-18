# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.c

Purpose: V4L2 mem2mem driver for Samsung S5P/Exynos G2D 2D accelerator. It exposes one mem2mem video node that copies, flips, inverts, crops/composes, and scales RGB buffers using the G2D hardware.

Important APIs and functions: `g2d_open()` allocates a per-file `g2d_ctx`, initializes source/destination vb2 queues, controls, and default frames. `vidioc_try_fmt()`, `vidioc_s_fmt()`, `vidioc_g_selection()`, and `vidioc_s_selection()` implement format and crop/compose negotiation. `device_run()` programs a job using `g2d-hw.c`; `g2d_isr()` completes source/destination buffers and the mem2mem job. `g2d_probe()` maps MMIO, prepares clocks, requests IRQ, registers V4L2/mem2mem/video devices, and selects v3/v4 variant data from OF match.

Control flow: userspace opens the node, configures source/output formats and selections, queues one source and one destination buffer, then V4L2 mem2mem calls `device_run()`. The driver enables the gate clock for the job, resets the engine, programs geometry and DMA addresses, applies ROP/flip controls under `ctrl_lock`, starts hardware, and waits for IRQ. The ISR clears the interrupt, disables the gate clock, removes both buffers, copies timestamp metadata, marks both done, finishes the job, and clears `dev->curr`.

State and persistence: global state is `struct g2d_dev` with V4L2/m2m devices, locks, clocks, MMIO, current context, and variant. Per-file state is `struct g2d_ctx` containing input/output `g2d_frame`s, controls, ROP, and flip flags. No persistent storage exists.

Dependencies and integration: V4L2 mem2mem core, vb2 DMA-contig, OF platform matching (`samsung,s5pv210-g2d`, `samsung,exynos4212-g2d`), `sclk_fimg2d` and `fimg2d` clocks, one IRQ, and hardware helpers from `g2d-hw.c`.

Risks: `vidioc_s_selection()` does not visibly clamp rectangles to frame bounds or nonzero dimensions beyond negative offset checks, so invalid crop/compose sizes can reach hardware and scaling division. `g2d_s_ctrl()` handles `V4L2_CID_HFLIP` cluster updates but has no explicit `V4L2_CID_VFLIP` case, relying on clustered HFLIP callback behavior. The ISR uses `BUG_ON()` for missing context/buffers, which can panic on unexpected IRQ or state corruption.

Test signals: `v4l2-compliance` mem2mem, RGB32/RGB565/RGB555/RGB444/RGB24 formats, crop/compose bounds including zero/oversize rectangles, negative effect control, H/V flip cluster, scaling on both hardware variants, IRQ storm/unexpected IRQ handling, and clock prepare/enable failure paths.
