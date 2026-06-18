# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.h

Purpose: Defines common STI plane descriptors, status states, FPS accounting, and helper prototypes.

Important types/APIs: `enum sti_plane_type`, `enum sti_plane_id_of_type`, and `enum sti_plane_desc` encode GDP0-3, HQVDP0, cursor, and background. `enum sti_plane_status` drives cross-module atomic flow (`READY`, `UPDATED`, `DISABLING`, `FLUSHING`, `DISABLED`). `struct sti_plane` embeds a DRM plane plus descriptor, status, and FPS info. `to_sti_plane()` converts DRM plane to STI plane. Helpers expose string conversion, FPS update, and property init.

Control/state: Status values are the handshake between plane atomic helpers and CRTC flush/VTG callbacks. `STI_PLANE_TYPE_MASK` lets code group GDP/VDP/cursor/background classes.

Dependencies/integration: Includes DRM atomic helper definitions and is included by nearly every STI plane/mixer/CRTC component.

Risks/test signals: Plane descriptor bit layout is relied on by comparisons such as overlay disable checks. Any enum change needs CRTC/mixer/GDP/HQVDP validation.
