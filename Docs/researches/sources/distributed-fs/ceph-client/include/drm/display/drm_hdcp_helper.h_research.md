# sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp_helper.h

Purpose: DRM HDCP helper declarations for KSV revocation checks and connector content-protection property handling.

Important APIs/types/functions: `drm_hdcp_check_ksvs_revoked`, `drm_connector_attach_content_protection_property`, and `drm_hdcp_update_content_protection`.

Control flow: drivers attach the content-protection property, check KSVs against SRM data during authentication/repeater validation, and update connector property state when protection changes.

State and persistence: no header state. Connector properties live in DRM core; HDCP/SRM state lives in implementations.

Dependencies and integration points: DRM devices/connectors, HDCP protocol definitions, userspace-visible content protection, and HDCP engines.

Risks and test signals: stale property state, missing content type support, and KSV count errors are risks. Test property attachment, authenticated/desired transitions, revoked KSVs, zero KSV count, and connector destruction during protection work.
