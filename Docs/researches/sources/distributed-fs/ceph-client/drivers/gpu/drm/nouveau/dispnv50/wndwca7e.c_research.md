
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwca7e.c

## Purpose
Implements the GB202/Blackwell CA7E window backend. It switches image, notifier, and ILUT programming from context-DMA handles to physical surface-address methods.

## Important APIs, types, and functions
- `wndwca7e_image_set()` programs ISO surface high/low physical address, target, kind, enable bit, present control, size, storage, params, planar storage, source point/size, and output size.
- `wndwca7e_image_clr()` disables the ISO surface address and programs non-tearing present control.
- `wndwca7e_ilut_set/clr()` program physical ILUT surface address and ILUT control.
- `wndwca7e_ntfy_set/clr()` program physical notifier address from `disp->sync->offset + asyw->ntfy.offset`.
- `wndwca7e_modifiers[]` advertises separate block-linear modifier sets for 4cpp+, 1cpp, and 2cpp layouts plus linear.
- `wndwca7e_new()` delegates construction to `wndwc37e_new_()`.

## Control flow
The common prepare path detects Blackwell by class and avoids creating CTXDMAs, filling a fake nonzero image handle only for enable-state tracking. At flush, CA7E methods use the BO's physical offset directly. The function table reuses C57E ILUT description/loading, C57E CSC, and C37E blend/update/acquire behavior while replacing the methods that need physical-address programming.

## State and persistence
Persistent hardware state is carried by physical address registers rather than context DMA objects. Common `struct nv50_wndw` still stores the DRM plane, DMA channel, notifier offset, LUT allocation, and interlocks. Modifier state is static.

## Dependencies and integration points
Depends on `wndw.h`, `atom.h`, `nvif/pushc97b.h`, `clca7e.h`, and Nouveau BO helpers. It integrates with the Blackwell branch in `nv50_wndw_prepare_fb()`.

## Risks
Physical-address programming increases alignment and address-width sensitivity; low addresses are shifted by four bits. Notifier and ILUT addresses derive from shared sync/LUT offsets, so any mismatch can corrupt synchronization or color state. CA7E omits semaphore callbacks in the function table; common code must only request semaphores when supported.

## Test signals
GB202 plane creation, physical-address scanout flips, notifier completion, ILUT set/clear, block-linear modifiers for 1/2/4cpp formats, and cleanup without CTXDMA destruction are key checks.
