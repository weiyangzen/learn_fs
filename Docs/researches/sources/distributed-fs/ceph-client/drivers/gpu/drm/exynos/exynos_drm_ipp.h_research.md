# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_ipp.h

Purpose: this header defines the internal IPP backend contract and task data structures shared by the common IPP core and hardware backends.

Important types: `struct exynos_drm_ipp_funcs` declares nonblocking `commit()` and asynchronous-safe `abort()` callbacks. `struct exynos_drm_ipp` stores DRM/device pointers, list id, name, callback table, caps, supported formats, sequence, lock, current task, todo list, and waitqueue. `struct exynos_drm_ipp_buffer` combines UAPI buffer/rectangle data with GEM references, DRM format info, and per-plane DMA addresses. `struct exynos_drm_ipp_task` stores source/destination buffers, transform, alpha, cleanup work, flags, return code, and optional event. `struct exynos_drm_ipp_formats` maps fourcc/modifier/type to hardware limits.

Control flow and integration: backends call `exynos_drm_ipp_register()` in component bind and provide commit/abort callbacks. Backends call `exynos_drm_ipp_task_done()` from IRQ or abort paths. The common IOCTL code uses the struct fields to validate and schedule tasks. Macros `IPP_SRCDST_FORMAT`, `IPP_SRCDST_MFORMAT`, `IPP_SIZE_LIMIT`, and `IPP_SCALE_LIMIT` simplify backend format tables.

State and persistence: this header defines runtime scheduler and task state. No persistence exists.

Dependencies: it relies on DRM Exynos UAPI structures, DRM format info through C files, Exynos GEM, and `MAX_FB_BUFFER` from the driver header.

Risks: backend `commit()` must not wait synchronously and must eventually call task-done or the queue stalls. `abort()` must also complete the task. Disabled `CONFIG_DRM_EXYNOS_IPP` stubs return empty resources or `-ENODEV`.

Test signals: compile with IPP enabled/disabled, backend registration/unregistration, macro-generated limits, task completion from IRQ and abort, and IOCTL stub behavior.
