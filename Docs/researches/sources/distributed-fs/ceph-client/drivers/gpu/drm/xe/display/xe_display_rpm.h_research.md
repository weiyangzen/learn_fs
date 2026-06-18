# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_rpm.h

Purpose: exports `xe_display_rpm_interface`. It has no runtime behavior or owned state. Integration points are the parent display interface and shared display runtime PM helpers. Risks are declaration/implementation drift. Test signals are build/link coverage and runtime PM path tests through `xe_display_rpm.c`.
