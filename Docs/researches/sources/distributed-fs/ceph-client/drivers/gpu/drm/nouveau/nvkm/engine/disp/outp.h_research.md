<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h

## Purpose

`outp.h` defines the private output-path data model and function-table contract for nouveau display outputs, including DCB metadata, acquisition state, LVDS/DP side state, user object embedding, and generic helpers.

## Important APIs, Types, And Functions

`struct nvkm_outp` stores `func`, `disp`, DCB index/info, I2C bus, connector, identity flag, acquisition bits (`NVKM_OUTP_PRIV` and `NVKM_OUTP_USER`), assigned IOR, LVDS flags, DP caps/link-training state, and asynchronous head pointer. `struct nvkm_outp_func` provides optional hooks for destructor/init/fini, detect, EDID, inherit/acquire/release, backlight, and DP AUX/rates/train/drive/MST methods. The header declares constructors, init/fini, detect, IOR acquire/release/inherit, backlight helpers, and output logging macros.

## Control Flow

The generic display code allocates an `nvkm_outp` with `nvkm_outp_new_()` or a specialized DP constructor. User methods and display modeset paths call the function-table hooks through this header's contract. Acquisition state flows from output object to IOR `asy` state and finally into supervisor routing/programming.

## State And Persistence Behavior

The output path persists for the display engine lifetime and caches both topology from VBIOS and dynamic link-training state. DP arrays record advertised rates, DPCD bytes, LTTPR data, AUX power state, MST status, and current training request. The `object` field is installed only while a userspace NVIF object has opened the output.

## Dependencies And Integration Points

The header includes DRM DP definitions and nouveau BIOS DCB/DP structures. It is used by generic output code, DP output implementation, user output methods, connector creation, and generation display files.

## Risks And Edge Cases

DP state in this structure is shared between kernel link management and userspace-facing NVIF methods; validation is needed before trusting userspace-provided rates, DPCD, or LTTPR counts. Acquisition bits allow private and user users to coexist, so release order matters.

## Test Signals

Build coverage catches function-table mismatches. Runtime signals include accurate output masks, DP train/rates calls updating cached state, correct acquire/release behavior, and no stale `object.func` exposure after destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h -->
