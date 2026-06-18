<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h

Purpose: header for the HDMI infoframe packing helper and packed register-word structure.

Important APIs and types: `struct packed_hdmi_infoframe` stores one `header` word and four subpacket words. `pack_hdmi_infoframe()` converts raw bytes into this structure. Including `ior.h` ties the helper to display output-resource code.

Control flow: none in the header; generation HDMI callbacks call the declared helper before writing registers.

State and persistence: none directly; instances are stack-local in callers.

Dependencies and integration points: included by generation SOR HDMI implementations. The struct field order mirrors common hardware write order in those files.

Risks: changing field names/order requires updates to all generation HDMI callbacks. The helper contract permits truncation and does not include validation metadata.

Test signals: build all HDMI callback users and validate packed values through `hdmi.c` tests or sink-visible infoframes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/hdmi.h -->
