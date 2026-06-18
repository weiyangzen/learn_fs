# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/disp.h

## Purpose
Declares the NVIF display object and its connector/output/head masks.

## Important APIs, Types, And Functions
Defines `struct nvif_disp` with embedded object and bit masks, plus `nvif_disp_ctor` and `nvif_disp_dtor`.

## Control Flow
Construction instantiates a display class object and receives masks that drive later connector/output/head enumeration.

## State And Persistence
The masks persist in the display wrapper while the DRM device enumerates display resources.

## Dependencies And Integration Points
Depends on `nvif/object.h` and device display classes in `class.h`; connects NVKM display objects to DRM resource creation.

## Risks
Incorrect masks hide resources or cause attempts to construct nonexistent child objects.

## Test Signals
Display probe resource counts, connector/output/head creation, and modeset smoke tests validate behavior.
