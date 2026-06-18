<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h

Purpose: provides the private include guard and pulls in DRM HDCP protocol definitions for `mei_hdcp.c`.

Important APIs and types: it includes `<drm/display/drm_hdcp.h>`, which supplies HDCP 2.2 message structures, constants, and helper declarations used by the MEI HDCP command translator.

Control flow: none; this is a compile-time dependency header.

State and persistence: no state.

Dependencies and integration: couples the MEI HDCP client to DRM display HDCP structures instead of duplicating protocol layouts locally. This keeps message fields aligned with display core expectations.

Risks: because the header currently contains no local declarations, changes to DRM HDCP headers can directly break `mei_hdcp.c`. Adding local command declarations here in the future would need careful separation from UAPI/DRM protocol structs.

Test signals: compile coverage of `mei_hdcp.c`, especially after DRM HDCP header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/mei_hdcp.h -->
