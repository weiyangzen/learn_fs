# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Makefile

Purpose: lists the object files that form the `logicvc-drm` module.

Important APIs/types/functions: `logicvc-drm-y` includes CRTC, DRM probe/core, interface, layer, mode, and OF parser objects. `obj-$(CONFIG_DRM_LOGICVC)` links them as `logicvc-drm.o`.

Control flow: build-system only; no runtime behavior.

State and persistence: build composition persists in generated objects/modules.

Dependencies and integration points: must match symbols declared across `logicvc_*.h`, especially probe calling layer/CRTC/interface/mode init in sequence.

Risks and test signals: omitting an object breaks unresolved symbols; adding stale objects breaks builds. Test module and built-in configurations.
