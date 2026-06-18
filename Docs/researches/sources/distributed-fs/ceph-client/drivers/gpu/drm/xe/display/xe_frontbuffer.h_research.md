# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_frontbuffer.h

Purpose: declares `xe_display_frontbuffer_interface`. It owns no state and has no control flow. Integration points are `xe_display.c` parent interface setup and shared frontbuffer tracking code. Risks are symbol drift and missing include type visibility at use sites. Test signals are build/link coverage and frontbuffer lifetime tests in `xe_frontbuffer.c`.
