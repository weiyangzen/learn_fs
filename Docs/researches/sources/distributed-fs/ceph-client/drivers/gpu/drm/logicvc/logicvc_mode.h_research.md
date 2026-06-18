# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_mode.h

Purpose: declares mode configuration lifecycle hooks for LogiCVC.

Important APIs/types/functions: `logicvc_mode_init` and `logicvc_mode_fini`.

Control flow: core probe calls init after CRTC/interface setup; remove calls fini before clock teardown.

State and persistence: no state in the header; mode state lives in `drm_device`.

Dependencies and integration points: forward-declares `logicvc_drm` and is included by the core DRM file.

Risks and test signals: lifecycle order must match probe/remove. Test probe failure unwinding after mode init.
