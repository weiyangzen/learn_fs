# sources/distributed-fs/ceph-client/include/drm/gud.h

Purpose: defines the public USB Generic Display protocol ABI shared by host and device firmware. It is entirely packed wire data and request/status constants, covering descriptor discovery, modes, connectors, properties, framebuffer transfers, state validation, and DPMS/controller enablement.

Important APIs/types/functions: `gud_display_descriptor_req`, `gud_property_req`, `gud_display_mode_req`, `gud_connector_descriptor_req`, `gud_set_buffer_req`, and variable-length `gud_state_req` are the exported protocol records. Constants cover display magic, protocol flags such as `GUD_DISPLAY_FLAG_STATUS_ON_SET` and `GUD_DISPLAY_FLAG_FULL_UPDATE`, LZ4 compression, connector types, mode flags compatible with DRM/RandR, TV/backlight/rotation properties, USB request numbers, pixel formats, connector status, EDID and mode limits, and status/error codes.

Control flow: consumers first fetch the descriptor, formats, properties, connector descriptors, connector properties, status, and modes/EDID. Runtime flow validates a full `gud_state_req` with `GUD_REQ_SET_STATE_CHECK`, commits with `GUD_REQ_SET_STATE_COMMIT`, and sends damage rectangles through `GUD_REQ_SET_BUFFER` followed by bulk data unless full-update mode suppresses per-transfer setup.

State and persistence: the header persists no kernel state, but its structures define device-visible state. The full display state is resent on each change; connector changed bits and status requests are explicit protocol synchronization points.

Dependencies and integration: depends only on Linux fixed-width types and packed layout. Integrated by DRM GUD host/gadget code and USB control/bulk transports.

Risks and test signals: ABI drift, endian mistakes, non-packed layout changes, invalid flexible-array sizing, and compression/full-update incompatibility are primary risks. Tests should validate descriptor parsing, unsupported status paths, connector hotplug semantics, mode flag masks, EDID length bounds, buffer rectangle bounds, and byte-exact protocol records.
