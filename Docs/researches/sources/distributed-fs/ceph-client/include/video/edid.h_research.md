<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/edid.h -->
# sources/distributed-fs/ceph-client/include/video/edid.h

Purpose: provides the kernel-side wrapper for the UAPI EDID block definition.

Important APIs and types: it includes `uapi/video/edid.h`, thereby exposing `struct edid_info` to kernel video code without defining additional symbols.

Control flow: kernel video/fbdev code includes this wrapper when it needs the legacy EDID UAPI container.

State and persistence: no state; all data is the raw EDID block passed through `edid_info`.

Dependencies and integration points: integrates UAPI EDID definitions into kernel include paths and legacy framebuffer display-probing code.

Risks and test signals: risks are include-path drift and assuming this wrapper provides EDID parsing helpers when it only exposes the raw container. Test compile coverage for video drivers including `video/edid.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/edid.h -->
