# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/display/xe_hdcp_gsc.h

Purpose: declares `xe_display_hdcp_interface`. There is no local state or control flow. Integration points are `xe_display.c` parent interface setup and shared Intel HDCP code. Risks are symbol drift only. Test signals are build/link coverage and HDCP GSC paths in `xe_hdcp_gsc.c`.
