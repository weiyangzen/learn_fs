# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_initial_plane.h

Purpose: exports `xe_display_initial_plane_interface`. It contains no runtime behavior or owned state. Integration points are `xe_display.c` and shared initial-plane takeover code. Risks are declaration drift. Test signals are build/link coverage and initial plane paths in `xe_initial_plane.c`.
