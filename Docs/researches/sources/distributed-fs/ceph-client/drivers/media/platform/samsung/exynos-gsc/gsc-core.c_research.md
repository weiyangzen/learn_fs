# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.c

Purpose: core implementation for the Samsung Exynos5 G-Scaler V4L2 mem2mem driver. It provides format tables, scaling/crop validation, V4L2 controls, DMA address preparation, IRQ handling, SoC variant data, platform probe/remove, and runtime PM.

Important APIs and functions: exported-to-driver helpers include `get_format`, `find_fmt`, `gsc_enum_fmt`, `gsc_try_fmt_mplane`, `gsc_g_fmt_mplane`, `gsc_try_selection`, `gsc_set_scaler_info`, `gsc_ctrls_create/delete`, `gsc_prepare_addr`, and `gsc_set_prefbuf`. Platform lifecycle is handled by `gsc_probe`, `gsc_remove`, runtime suspend/resume, and `gsc_irq_handler`.

Control flow: probe reads OF match data and alias ID, chooses a per-entity variant, maps registers, gets/enables clocks, requests IRQ, registers V4L2 and mem2mem devices, resets hardware, sets DMA segment limits, and enables PM runtime. User format/selection/control operations call this file to clamp dimensions, compute prescaler/main-scaler ratios, maintain context state, and calculate plane payload/DMA addresses. IRQ handling clears frame-done or overrun status, finalizes active m2m jobs, and handles suspend transitions.

State and persistence: device state includes locks, clocks, MMIO base, waitqueue, m2m device, V4L2 device, and variant pointer. Context state includes source/destination frames, crop, scaler ratios, rotation/flip/alpha controls, colorspace, and state flags. Hardware state is reset on probe and runtime resume.

Dependencies and integration points: depends on V4L2/vb2 APIs, platform/OF, clocks, PM runtime, `gsc-core.h`, `gsc-regs.h`, and the sibling `gsc-m2m.c`/`gsc-regs.c` implementation.

Risks: many calculations mutate requested crop/format values to hardware alignment; callers must handle adjusted rectangles. Scaling ratio limits are variant-dependent and can reject rotations differently. Probe enables clocks before PM runtime and must unwind carefully. `gsc_set_prefbuf` only logs computed ranges in this snapshot. IRQ and suspend state depend on spinlock-protected flags.

Test signals: v4l2-compliance for mem2mem, format enumeration/try/set across all supported formats, crop/rotation/scale boundary tests per Exynos variant, IRQ completion/overrun tests, runtime suspend/resume during active and idle queues, and DMA address validation for one-, two-, and three-plane formats.
