# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.h

Purpose: declares LogiCVC layer/plane configuration structures and layer helper APIs.

Important APIs/types/functions: layer colorspace/alpha constants, `struct logicvc_layer_buffer_setup`, `struct logicvc_layer_config`, `struct logicvc_layer_formats`, `struct logicvc_layer`, and lookup/init/attach helpers.

Control flow: no executable flow; defines the data contract used by layer parsing and plane updates.

State and persistence: per-layer runtime state includes parsed DT config and associated DRM plane. Buffer setup is transient output from offset computation.

Dependencies and integration points: includes OF and DRM plane headers and is shared by core, CRTC, and layer code.

Risks and test signals: fields must remain synchronized with `logicvc_of.c` property parser and `logicvc_layer.c` format tables. Test DT parsing and plane creation with varied layer depths and alpha modes.
