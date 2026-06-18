# sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp.h

Purpose: shared HDCP 1.x and HDCP 2.2 constants, register offsets, message IDs, timeout values, packed protocol messages, SRM formats, and helper conversions for HDMI/DVI/DP content protection.

Important APIs/types/functions: HDCP check periods, KSV/AN/Ri/Bstatus lengths, DDC offsets, HDCP 2.2 message IDs/field lengths/timeouts/registers, stream type constants, SRM constants, packed message structs including AKE, LC, SKE, repeater messages, `hdcp_srm_header`, and inline 24-bit big-endian sequence conversion helpers.

Control flow: authentication code composes/parses messages, polls readiness using timeouts, processes repeater KSV/receiver lists, manages stream types, and validates SRM revocation data using these definitions.

State and persistence: no mutable header state. Session keys, nonces, sequence numbers, and authentication status live in drivers/hardware; packed structs are protocol byte-layout contracts.

Dependencies and integration points: Linux types/endian annotations, DRM connector content protection, DP DPCD HDCP offsets, HDMI DDC registers, SRM revocation, and HDCP hardware/TEE engines.

Risks and test signals: packed layout errors, HDMI/DP timeout mismatch, endian bugs, repeater count/depth mask errors, and fixed stream-count assumptions are risks. Test HDCP 1.4/2.2, repeaters, SRM revocation, Type0/Type1 streams, DP/HDMI transports, timeouts, and sequence rollover.
