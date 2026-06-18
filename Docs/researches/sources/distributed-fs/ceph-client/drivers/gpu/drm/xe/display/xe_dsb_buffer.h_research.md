# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_dsb_buffer.h

Purpose: declares `xe_display_dsb_interface`. No local state or control flow exists. Integration points are `xe_display.c` parent interface setup and display DSB users. Risks are limited to symbol drift. Test signals are build/link coverage and DSB command-buffer paths.
