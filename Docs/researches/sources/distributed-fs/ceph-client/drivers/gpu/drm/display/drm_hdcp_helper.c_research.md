# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdcp_helper.c

Purpose: centralizes DRM HDCP content-protection property creation, HDCP SRM firmware parsing, KSV revocation checks, and kernel-originated content protection state notifications.

Important APIs/types/functions: exports `drm_hdcp_check_ksvs_revoked`, `drm_connector_attach_content_protection_property`, and `drm_hdcp_update_content_protection`. Internal helpers parse HDCP 1.4 and HDCP 2.x SRM blobs, read big-endian 24-bit VRL lengths, count/copy revoked KSVs, and expose enum-name helpers through `DRM_ENUM_NAME_FN` for content protection and HDCP content type values.

Control flow: `drm_hdcp_check_ksvs_revoked` calls `drm_hdcp_request_srm`, which requests `display_hdcp_srm.bin` with `request_firmware_direct`. If no firmware is present, it treats the revocation list as empty. If firmware exists, `drm_hdcp_srm_update` identifies HDCP 1.4 or 2.x by the SRM ID byte and dispatches to the matching parser. HDCP 1.4 parsing walks VRL records containing a count byte followed by 5-byte KSVs and validates total parsed length; HDCP 2.x parsing derives the KSV count from the HDCP 2 count/reserved fields and copies one contiguous KSV array. The exported checker then compares each caller KSV with each revoked KSV and returns the number of matches. Property attachment lazily creates global mode_config enum properties and attaches them to the connector with default values. `drm_hdcp_update_content_protection` updates the live connector state and emits a sysfs property event.

State and persistence: SRM data is loaded per call from firmware and freed immediately. Created DRM properties persist in `dev->mode_config`. Connector state fields `content_protection` and `hdcp_content_type` persist through atomic state; update notification requires the connection mutex to be held.

Dependencies and integration: uses Linux firmware loading, allocation, DRM property/mode object helpers, sysfs connector property events, and HDCP constants from DRM display headers. Display drivers call these helpers when exposing HDCP support and when authentication transitions between desired/enabled states.

Risks: SRM parsing is security-sensitive binary parsing of firmware-provided data. Length checks must prevent malformed VRLs from causing out-of-bounds reads; HDCP 2 parsing relies on SRM length constraints before copying. A missing firmware file intentionally means no revoked KSVs, which is operationally permissive. Property updates warn if modeset locking is missing and can desynchronize userspace if drivers call them outside the documented state transitions.

Test signals: useful tests include malformed/short SRM blobs, reserved bit handling, zero KSV lists, duplicate matches, firmware-not-found behavior, property attachment with and without HDCP content type, and sysfs uevent emission after kernel-triggered content protection changes.
