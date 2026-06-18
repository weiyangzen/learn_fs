# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_bo.h

Purpose: exports `xe_display_bo_interface` to the display parent interface. It contains no control flow or state beyond the extern declaration. Dependencies are the interface type declaration from display parent code at use sites. Integration points are `xe_display.c` parent interface initialization and framebuffer/display BO operations. Risks are limited to symbol/prototype drift if the implementation changes. Test signals are build/link coverage and display framebuffer creation paths.
