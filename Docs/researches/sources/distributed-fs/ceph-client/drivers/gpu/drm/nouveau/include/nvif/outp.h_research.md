# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/outp.h

## Purpose
Declares the NVIF output object wrapper and high-level output operations for display connectors.

## Important APIs, Types, And Functions
Defines `struct nvif_outp`, output type/protocol enums, DDC/connector info, OR acquisition state, detect enum, EDID/load/acquire/inherit/release APIs, backlight, LVDS, HDMI, infoframe, HDA ELD, DP AUX, rates, training, drive, SST, MST ID, and VCPI APIs.

## Control Flow
Callers construct outputs, detect sinks, get EDID, acquire an output resource, configure protocol-specific state, perform DP link training/AUX/MST, and release the resource when no longer used.

## State And Persistence
Output state stores id, hardware type/protocol, caps, DP link data, and acquired OR id/link until release or destruction.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/if0012.h`, and DRM DP definitions; integrated with Nouveau DRM encoder/connector code.

## Risks
Acquire/release balance, protocol selection, DP training parameters, and MST allocation are high-risk display paths.

## Test Signals
Connector detection, EDID, HDMI/DP/eDP/LVDS modesets, backlight, AUX, MST, and hotplug tests validate behavior.
