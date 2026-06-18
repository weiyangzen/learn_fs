
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc37e.c

## Purpose
Implements the GV100/C37E display window channel backend. It provides base window programming for semaphores, notifiers, input LUT, CSC, image surfaces, blending, and update interlocks.

## Important APIs, types, and functions
- LUT/CSC: `wndwc37e_ilut()`, `wndwc37e_ilut_set()`, `wndwc37e_ilut_clr()`, `wndwc37e_csc_set()`, and no-op `wndwc37e_csc_clr()`.
- Image: `wndwc37e_image_set()` and `wndwc37e_image_clr()`.
- Synchronization: `wndwc37e_ntfy_set/clr()`, `wndwc37e_sema_set/clr()`, `wndwc37e_update()`.
- Plane validation: `wndwc37e_acquire()` delegates to `drm_atomic_helper_check_plane_state()` with no scaling limits beyond exact no-scaling constraints.
- `wndwc37e_format[]` lists C8, packed YUV, RGB565, 1555/8888/2101010, and FP16 formats.
- `wndwc37e_new_()` creates the DRM plane and display DMA channel; `wndwc37e_new()` supplies the C37E function table and head mask.

## Control flow
Common atomic code derives `nv50_wndw_atom` state, then this backend serializes that state to NVC37E methods. Image set programs present mode, size/storage/params, planar storage, context DMA, offset, source point, source size, and destination size. Blend set programs depth, alpha, blend factors, and disables color keying by opening key ranges. Update combines core/cursor/window/WIMM interlock flags before kicking the channel.

## State and persistence
The backend creates `wndw->wndw`, initializes notification and semaphore offsets, and writes persistent display channel state. LUT data lives in the common `nv50_lut` object; this backend points hardware at the LUT context DMA and offset.

## Dependencies and integration points
Uses `wndw.h`, `atom.h`, DRM atomic helper, Nouveau BO, `nvif/if0014.h`, `nvif/pushc37b.h`, and `clc37e.h`. It serves as the base implementation reused by C57E/C67E/CA7E variants.

## Risks
Method counts in `PUSH_WAIT()` must match emitted words. The C37E CSC clear is a no-op, so callers rely on image parameters or later programming to disable effects. Pitch and block count share a field macro path and require correct common-state derivation. The error message says `qndw` rather than `wndw`, which can confuse diagnostics.

## Test signals
GV100 window creation, framebuffer flips, LUT/CSC programming, alpha/blend behavior, semaphore/notifier synchronization, and interlock updates provide coverage. Atomic helper failures should reject unsupported scaling/position combinations.
