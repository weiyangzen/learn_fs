# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_panic.h

Purpose: declares `xe_display_panic_interface` for the display parent interface. No local state or control flow exists. Integration points are `xe_display.c` and DRM panic support. Risks are symbol drift. Test signals are build/link coverage and panic rendering paths in `xe_panic.c`.
