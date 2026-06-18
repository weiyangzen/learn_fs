# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_stolen.h

Purpose: declares `xe_display_stolen_interface`. It owns no state and has no control flow. Integration points are `xe_display.c` and shared display stolen-memory users. Risks are declaration drift only. Test signals are build/link coverage and stolen allocation tests in `xe_stolen.c`.
