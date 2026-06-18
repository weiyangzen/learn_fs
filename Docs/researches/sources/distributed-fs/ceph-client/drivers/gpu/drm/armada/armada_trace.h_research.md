## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_trace.h

Purpose: declares Armada DRM trace events for interrupt handling and overlay plane activity.

Important tracepoints are `armada_drm_irq`, recording a CRTC pointer and IRQ status word; `armada_ovl_plane_update`, recording plane/CRTC/framebuffer pointers and destination/source rectangles; and `armada_ovl_plane_work`, recording plane and CRTC pointers. `TRACE_SYSTEM` is `armada`, and `TRACE_INCLUDE_PATH` is set relative to the driver tree for generated trace code.

Control flow is tracing-only: event call sites populate entries with `TP_fast_assign`, and `TP_printk` formats pointer/status/geometry details. State persists only in enabled trace buffers. Dependencies are Linux tracepoint macros and forward-declared DRM objects.

Risks include pointer-only trace data limiting postmortem interpretation, path fragility if the file moves, and source coordinates printed after 16.16 fixed-point shifts. Test signals are tracepoint compilation, `trace_armada_*` symbols resolving, and useful trace output during overlay commits and IRQs.
