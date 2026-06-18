# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_display_pcode.h

Purpose: declares `xe_display_pcode_interface` for registration in the display parent interface. There is no local control flow or state. Integration points are `xe_display.c` and shared display pcode users. Risks are symbol drift only. Test signals are build/link coverage and pcode-using display paths.
