# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_drm.h

Purpose: defines top-level LogiCVC configuration, capability, and device structures.

Important APIs/types/functions: display interface/colorspace constants, `logicvc_drm(d)` container helper, `struct logicvc_drm_config`, `struct logicvc_drm_caps`, and `struct logicvc_drm`.

Control flow: no executable flow; probe fills config/caps and submodules consume fields during mode, layer, and interface initialization.

State and persistence: `logicvc_drm` is the runtime state root: DRM device, reserved memory base, regmap, clocks, layer list, CRTC pointer, and interface pointer.

Dependencies and integration points: includes Linux regmap and DRM device definitions. Shared by all LogiCVC C files.

Risks and test signals: config semantics must match DT parser and layer/interface users. Test multiple IP versions and display interfaces.
