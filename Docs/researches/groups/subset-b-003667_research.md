# subset-b-003667 research

Grouped research for Nouveau NV50+ display window, overlay, SOR/PIOR, immediate-window, GV100 fence, I2C encoder, firmware descriptor, and hardware class definition files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly907e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly907e.c

## Purpose
Implements the NV907E overlay window backend used by Nouveau display code. It supplies the `nv50_wndw_func` method table for a 90-series overlay channel and creates overlay planes with the supported DRM formats.

## Important APIs, types, and functions
- `ovly907e_image_set()` writes NV907E present, DMA context, composition, surface offset, size, storage, format, and color-space methods.
- `const struct nv50_wndw_func ovly907e` wires common overlay helpers (`ovly507e_acquire`, `ovly507e_release`, `base507c_*`, `ovly827e_*`) to the NV907E image setter.
- `ovly907e_format[]` permits YUYV, UYVY, XRGB8888, XRGB1555, XBGR2101010, and XBGR16161616F.
- `ovly907e_new()` calls `ovly507e_new_()` with the overlay head mask `0x00000004 << (head * 4)`.

## Control flow
Plane creation is delegated to the shared 507E overlay constructor with this file's function table and format list. During an atomic flush, the generic overlay path calls `ovly907e_image_set()` after `nv50_wndw` state has prepared `asyw->image`. The function reserves push space, programs ASAP present control with the requested minimum present interval, binds the ISO DMA handle, forces opaque composition, and describes a single surface plane.

## State and persistence
The file owns no persistent state. It serializes fields already stored in `struct nv50_wndw_atom`, including `handle[0]`, `offset[0]`, dimensions, pitch/block layout, format, color space, and interval, into the display engine channel. Those hardware methods persist until replaced or cleared by shared `base507c_image_clr()`.

## Dependencies and integration points
Depends on `ovly.h`, `atom.h`, `nvif/push507c.h`, and `nvhw/class/cl907e.h`. It integrates with the shared NV50 overlay infrastructure, DRM plane format selection, and the display pushbuffer/interlock update path.

## Risks
The storage method writes both `PITCH` fields from block count and pitch expressions, so the method definition must match the generated class field aliases. Offset and pitch are shifted by eight bits, making alignment assumptions important. Format support is narrow and must match both DRM format validation and the NV907E hardware format field.

## Test signals
Build coverage catches method/class mismatches. Runtime signals are overlay plane enablement on supported GPUs, correct format/color output, no pushbuffer reservation failures, and successful atomic flips with non-tearing interval changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly907e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly917e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly917e.c

## Purpose
Defines the NV917E overlay constructor variant. It reuses the NV907E overlay implementation while expanding the advertised DRM format list.

## Important APIs, types, and functions
- `ovly917e_format[]` includes the NV907E formats plus `DRM_FORMAT_XRGB2101010`.
- `ovly917e_new()` calls `ovly507e_new_(&ovly907e, ovly917e_format, ...)`.

## Control flow
There is no independent programming path. Construction selects the wider format array, while all acquire, notification, image, scale, and update callbacks come from the `ovly907e` function table and shared overlay helpers.

## State and persistence
No state is stored here. Runtime state is held in `struct nv50_wndw` and `struct nv50_wndw_atom` by the common overlay code.

## Dependencies and integration points
Depends on `ovly.h` and on `ovly907e` being visible from the overlay backend set. This file is an integration shim for GPUs exposing the 917E overlay class but compatible with the 907E method sequence.

## Risks
The main compatibility risk is advertising `XRGB2101010` only when the underlying class and `ovly907e_image_set()` format mapping can represent it correctly. Any divergence between 917E hardware and 907E method layout would break at runtime because the same callbacks are reused.

## Test signals
Plane enumeration should show the additional 10-bit RGB format. Atomic overlay flips in both shared and added formats are the useful runtime check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly917e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/pior507d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/pior507d.c

## Purpose
Implements PIOR output-resource control for NV507D-era display core channels. PIORs drive external encoders such as external TMDS or TV encoders.

## Important APIs, types, and functions
- `pior507d_ctrl()` merges caller-provided control bits with hsync/vsync polarity and pixel depth from `struct nv50_head_atom`.
- `pior507d_get_caps()` marks `outp->caps.dp_interlace = true`.
- `const struct nv50_outp_func pior507d` exposes `.ctrl` and `.get_caps`.

## Control flow
When an output resource is assigned or reprogrammed, the core output path calls `.ctrl`. If a head atom is supplied, polarity and depth are encoded into `ctrl`; then `PIOR_SET_CONTROL(or)` is emitted on the core push channel. Capability discovery simply reports DP interlace support without probing hardware.

## State and persistence
The file does not keep software state. It changes PIOR control register state in the display core channel, and sets capability bits on the `nouveau_encoder` object during output initialization.

## Dependencies and integration points
Uses `core.h`, `nvif/push507c.h`, `cl507d.h`, and `cl837d.h`. It is selected by the NV50 display output table and relies on `nv50_head_atom` ownership/depth fields being precomputed by atomic modeset code.

## Risks
The function combines NV507D and NV837D field definitions for pixel depth; field compatibility is assumed. Always enabling DP interlace support may overstate capability if a future PIOR path has stricter limits.

## Test signals
Modeset tests through PIOR-backed encoders should verify polarity, depth, and owner/protocol programming. Compile-time class macro compatibility is also important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/pior507d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor507d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor507d.c

## Purpose
Implements SOR output-resource control for NV507D-era display core channels. SORs drive LVDS, TMDS, DisplayPort, and related serial display links.

## Important APIs, types, and functions
- `sor507d_ctrl()` writes `SOR_SET_CONTROL(or)` with optional hsync/vsync polarity and pixel depth from the head atom.
- `sor507d_get_caps()` sets `outp->caps.dp_interlace = true`.
- `const struct nv50_outp_func sor507d` exports the backend callbacks.

## Control flow
The output manager passes prebuilt owner/protocol bits in `ctrl`. This implementation augments those bits when a target head atom is available, reserves two push words, and emits the SOR control method. Capability initialization is static.

## State and persistence
No private state exists. SOR ownership, protocol, polarity, and depth persist in the display core until a later modeset rewrites them.

## Dependencies and integration points
Depends on `core.h`, `nvif/push507c.h`, `cl507d.h`, and `cl837d.h`. It integrates with NV50 core display resource assignment and the encoder capability model.

## Risks
Incorrect control bit composition can route an output to the wrong head or program an invalid protocol/depth combination. The static interlace capability should remain aligned with SOR class behavior.

## Test signals
Useful tests are SOR-backed HDMI/DVI/DP modesets, polarity-sensitive modes, bpc/depth changes, and interlaced DP mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor507d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor907d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor907d.c

## Purpose
Provides SOR control and capability probing for NV907D-era display core channels.

## Important APIs, types, and functions
- `sor907d_ctrl()` emits `NV907D_SOR_SET_CONTROL(or)` with the caller-provided control word.
- `sor907d_get_caps()` reads the display sync notifier BO with `NVBO_RV32()` and extracts the SOR DP interlace capability bit.
- `const struct nv50_outp_func sor907d` publishes the callbacks.

## Control flow
Unlike the 507D backend, this control function does not patch in polarity/depth from the head atom; it assumes the caller's `ctrl` already encodes the required state for the 907D class. Capability probing reads per-OR notifier capability data at `or * 2`.

## State and persistence
The file persists only hardware SOR control state. It also caches the discovered DP interlace capability in `nouveau_encoder->caps`.

## Dependencies and integration points
Uses `core.h`, `nvif/class.h`, `nvif/push507c.h`, `cl907d.h`, and `nouveau_bo.h`. It depends on the core notifier buffer being initialized with capability data before `get_caps` runs.

## Risks
Capability extraction depends on notifier layout and `or * 2` indexing; wrong offsets produce false capability reports. Omitting head atom-derived polarity/depth is correct only if higher-level code supplies class-appropriate bits.

## Test signals
Boot logs and encoder capabilities should reflect per-SOR DP interlace support. Runtime modesets should verify no regressions in polarity/depth on 907D-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor907d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sorc37d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sorc37d.c

## Purpose
Implements SOR output control for GV100/Turing-era C37D display core classes and reads SOR capabilities through the NVIF caps object.

## Important APIs, types, and functions
- `sorc37d_ctrl()` emits `NVC37D_SOR_SET_CONTROL(or)`.
- `sorc37d_get_caps()` reads `disp->caps` at `0x000144 + (or * 8)` and maps bit `0x04000000` to `dp_interlace`.
- `const struct nv50_outp_func sorc37d` exports the backend.

## Control flow
The display output code calls `.ctrl` with an already-formed control word; this file only serializes it into the core push channel. Capability probing uses `nvif_rd32()` instead of the older notifier BO path.

## State and persistence
No local state is retained. The output control method changes hardware core state; `get_caps` stores a boolean in the encoder capability cache.

## Dependencies and integration points
Depends on `core.h`, `nvif/pushc37b.h`, and `clc37d.h`. It integrates with the newer display caps object used by GV100+ display initialization.

## Risks
The raw caps offset and bit mask are hardware-contract details. Incorrect offsets silently misreport interlace support. Control words must be prepared by callers because this backend does not add polarity or depth fields.

## Test signals
DP interlace support should match hardware caps across SOR instances. Modeset tests should exercise SOR owner/protocol changes on C37D-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sorc37d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/tile.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/tile.h

## Purpose
Defines inline helpers for NVIDIA block-linear tiling geometry used by display scanout and panic scanout writes.

## Important APIs, types, and functions
- Constants: `NV_TILE_GOB_HEIGHT_TESLA`, `NV_TILE_GOB_HEIGHT`, and `NV_TILE_GOB_WIDTH_BYTES`.
- `nouveau_get_width_in_blocks()` converts byte stride to 64-byte GOB columns.
- `nouveau_get_gob_height()` returns Tesla versus Fermi+ GOB height.
- `nouveau_get_height_in_blocks()` rounds pixel height to block rows.
- `nouveau_get_gob_size()` returns bytes per GOB.
- `nouveau_get_gobs_in_block()` decodes log2 block height from tile mode, with chipset-specific bit handling.
- `nouveau_check_tile_mode()` validates the tile mode against chipset-specific maximum block height.

## Control flow
All helpers are static inline arithmetic. They branch on GPU family/chipset thresholds to account for Tesla GOB height, pre-C0 tile mode fields, and the wider block-height encoding used by newer chips.

## State and persistence
No state is stored. The helpers derive geometry from caller-supplied stride, height, tile mode, family, and chipset.

## Dependencies and integration points
Uses `nvif/device.h` for chipset/family constants. `wndw.c` uses these helpers for DRM panic scanout pixel placement and modifier validation paths depend on matching tiling semantics elsewhere in Nouveau.

## Risks
Off-by-one rounding or wrong chipset thresholds corrupt block-linear addressing. Panic rendering currently assumes limited formats, so these helpers must remain consistent with `nouveau_framebuffer_get_layout()` and DRM modifier encodings.

## Test signals
Validation signals include correct display of tiled framebuffers, successful panic text rendering on tiled scanout, and modifier acceptance/rejection tests for pre-C0, C0+, and Blackwell-era layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/tile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.c

## Purpose
Selects and initializes the display window immediate channel used to move a window's output point independently from the main window DMA channel.

## Important APIs, types, and functions
- `nv50_wimm_init()` selects among GB202, GA102, TU102, and GV100 `DISP_WINDOW_IMM_CHANNEL_DMA` classes.
- The local `wimms[]` table maps all supported immediate channel classes to `wimmc37b_init()`.

## Control flow
At the end of `nv50_wndw_new()`, the display code calls `nv50_wimm_init()`. It asks `nvif_mclass()` which immediate class the display object supports, reports an error if none match, and invokes the selected initializer.

## State and persistence
No persistent state is stored in this file. The selected initializer creates `wndw->wimm`, fills `wndw->immd`, and configures immediate interlock state.

## Dependencies and integration points
Depends on `wimm.h` and `nvif/class.h`. It is tightly integrated with `wndw.c` window creation and `nv50_wndw_flush_set()`, which calls `wndw->immd->point()` and `update()` when plane position changes.

## Risks
Failure to allocate a WIMM channel makes window creation fail even if the main window channel exists. The class table assumes all listed hardware generations can use the C37B-style implementation.

## Test signals
Plane creation on GV100, TU102, GA102, and GB202 classes should allocate immediate channels. Moving a visible plane without changing its image should exercise WIMM point updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.h

## Purpose
Declares the window immediate-channel initialization APIs used by `wndw.c`.

## Important APIs, types, and functions
- `nv50_wimm_init(struct nouveau_drm *drm, struct nv50_wndw *)`.
- `wimmc37b_init(struct nouveau_drm *, s32, struct nv50_wndw *)`.
- Includes `wndw.h` so callers see `struct nv50_wndw`.

## Control flow
No runtime control flow exists. It exposes the class selector and the concrete C37B initializer.

## State and persistence
No state is defined here. Implementations mutate `struct nv50_wndw` by creating the WIMM DMA channel and assigning the `nv50_wimm_func` table.

## Dependencies and integration points
This header is the narrow bridge between generic window creation and immediate-channel backends.

## Risks
Because it includes `wndw.h`, include-order or circular dependency changes require care. Signature drift would fail at build time.

## Test signals
Compile coverage is the primary signal. Runtime coverage comes from successful `nv50_wimm_init()` during window creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimmc37b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimmc37b.c

## Purpose
Implements the C37B-style window immediate channel backend. It programs fast output-position changes and interlocks them with the main window channel.

## Important APIs, types, and functions
- `wimmc37b_point()` writes `NVC37B_SET_POINT_OUT(0)` from `asyw->point`.
- `wimmc37b_update()` emits `NVC37B_UPDATE` with optional interlock against the main window.
- `wimmc37b_init_()` creates the immediate DMA channel and installs the function table.
- `wimmc37b_init()` is the exported concrete initializer.
- `static const struct nv50_wimm_func wimmc37b` supplies `.point` and `.update`.

## Control flow
Initialization creates a display DMA channel for the same window id, without a sync offset, then records the immediate interlock bit and function table. At flush time, `nv50_wndw_flush_set()` writes a point update when only the output position changes or when point state is dirty, then kicks the immediate channel update.

## State and persistence
The backend persists `wndw->wimm` and `wndw->immd`. Hardware point-out state persists in the immediate channel until updated. Interlock flags coordinate visibility of WIMM and main window changes.

## Dependencies and integration points
Depends on `wimm.h`, `atom.h`, `wndw.h`, `nvif/if0014.h`, `nvif/pushc37b.h`, and `clc37b.h`. It integrates with the atomic plane position path and display interlock bookkeeping.

## Risks
Interlock mismatches can make position updates race with image updates. `PUSH_KICK()` failures propagate through update, so callers must handle atomic commit errors. Channel allocation failure blocks window creation.

## Test signals
Move-only atomic commits should update plane position without full image reprogramming. Interlock tests should verify no tearing or stale coordinates when image and point change together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimmc37b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.c

## Purpose
Implements the common NV50+ DRM plane/window core for Nouveau display. It handles DRM plane lifecycle, atomic checking, framebuffer pinning, context DMA creation, LUT/CSC/blend/image state derivation, panic scanout mapping, format modifier validation, and generation-specific window class selection.

## Important APIs, types, and functions
- Context DMA helpers: `nv50_wndw_ctxdma_new()` and `nv50_wndw_ctxdma_del()`.
- Flush helpers: `nv50_wndw_flush_set()`, `nv50_wndw_flush_clr()`, `nv50_wndw_ntfy_enable()`, and `nv50_wndw_wait_armed()`.
- Atomic helpers: `nv50_wndw_atomic_check()`, `nv50_wndw_atomic_check_acquire()`, `nv50_wndw_atomic_check_lut()`, release/acquire RGB/YUV format mapping helpers.
- FB lifecycle: `nv50_wndw_prepare_fb()` pins BOs and sets image handles/offsets; `nv50_wndw_cleanup_fb()` unpins.
- DRM panic helpers: `nv50_wndw_get_scanout_buffer()`, `nv50_set_pixel()`, and `nv50_set_pixel_swizzle()`.
- Plane lifecycle: `nv50_wndw_reset()`, duplicate/destroy-state, `nv50_wndw_destroy()`, and `const struct drm_plane_funcs nv50_wndw`.
- Creation APIs: `nv50_wndw_new_()` and `nv50_wndw_new()`.

## Control flow
Plane creation picks the newest supported window class from GB202, GA102, TU102, and GV100, calls the generation-specific constructor, then initializes WIMM. The generic constructor allocates the DRM plane, installs helper funcs, creates LUT storage for windows with ILUT support, and exposes zpos/alpha/blend properties when hardware blending is available.

During atomic check, the code fetches new and old CRTC/head atoms, decides visibility, recalculates LUT/CSC when needed, and either acquires or releases hardware window state. Acquire maps DRM formats to display formats, derives pitch or block-linear storage parameters, chooses non-tearing versus immediate present mode from async flip state, computes scaling/blending/point dirty state, and delegates class-specific validation. Release clears handles and asks the backend to release resources. Modesets and disables mark old notifier, semaphore, LUT, CSC, and image state for clearing.

During prepare, the framebuffer BO is pinned to VRAM, a matching context DMA is created or reused for pre-Blackwell hardware, a fake enable handle is used for Blackwell's physical-address path, GEM plane preparation runs, and the scanout offset is recorded. Flush code then calls class-specific clear/set callbacks and updates display interlocks. Point-only changes are routed through the WIMM immediate channel.

## State and persistence
Persistent state lives in `struct nv50_wndw`: function pointers, window id, interlock data, context DMA object list, DRM plane, LUT allocation, main/WIMM DMA channels, notifier offsets, semaphore offsets, and cached data. Atomic state persists in `struct nv50_wndw_atom` fields copied by duplicate-state. Hardware state persists in display window methods until explicit clear or reprogram. Framebuffer BO pinning persists from prepare to cleanup.

## Dependencies and integration points
Depends on DRM atomic, blend, framebuffer, GEM plane helper, panic, and TTM mapping APIs; Nouveau BO/GEM/framebuffer helpers; NVIF DMA object creation; display interlocks; `tile.h`; generation backends `wndwc37e`, `wndwc57e`, `wndwc67e`, and `wndwca7e`; and WIMM initialization. It is the central integration point between DRM plane state and Nouveau display hardware channels.

## Risks
This file is high risk. Incorrect atomic dirty tracking can leave stale LUT/CSC/image state. Context DMA handle reuse is keyed by framebuffer kind, so layout extraction must be accurate. BO pin/unpin error paths must stay balanced; note that failures after `drm_gem_plane_helper_prepare_fb()` or backend `prepare()` rely on DRM cleanup behavior. Format modifier validation differs by chipset and can accidentally expose unsupported block-linear layouts. Panic scanout only supports single-plane uncompressed buffers and limited tiled 32-bit formats. The assignment inside `if (asyw->set.point = false, asyw->set.mask)` is intentional comma-expression clearing but easy to misread.

## Test signals
Useful signals include DRM atomic logs (`NV_ATOMIC`), successful plane creation per generation, primary/overlay/cursor flips, async flips, C8 legacy gamma behavior, degamma/CTM updates, zpos/alpha/blend modes, tiled and linear scanout, panic text rendering, modifier acceptance tests, BO pin leak checks, and WIMM move-only commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.h

## Purpose
Declares the common Nouveau NV50+ display window structures, callback interfaces, helper APIs, and generation-specific constructors.

## Important APIs, types, and functions
- `struct nv50_wndw_ctxdma` stores a context DMA object in a per-window list.
- `struct nv50_wndw` embeds the DRM plane plus display DMA channels, interlock state, LUT storage, notification/semaphore offsets, and callback pointers.
- `struct nv50_wndw_func` describes class-specific acquire/release, prepare, semaphore, notifier, LUT, CSC, image, scale, blend, and update operations.
- `struct nv50_wimm_func` describes immediate-channel point and update operations.
- Declares shared helpers such as `nv50_wndw_new_()`, `nv50_wndw_flush_set()`, `nv50_wndw_flush_clr()`, `nv50_wndw_ntfy_enable()`, and `nv50_wndw_wait_armed()`.
- Declares generation constructors and callbacks for C37E, C57E, C67E, CA7E, and generic `nv50_wndw_new()`.
- Inline `nvif_chan_wait()` adapts WIMM channel space checks to the NVIF push path.

## Control flow
The header has only the `nvif_chan_wait()` inline branch: it returns success when `curs507a_space(wndw)` reports room and `-ETIMEDOUT` otherwise. Runtime control flow is provided by implementations through the callback tables.

## State and persistence
The header defines the layout of persistent window state and the callback contract for hardware state programming. Atomic per-commit state is referenced through `struct nv50_wndw_atom` from `atom.h`.

## Dependencies and integration points
Includes `disp.h`, `atom.h`, and `lut.h`; exports `const struct drm_plane_funcs nv50_wndw`; and bridges common window code, cursor/immediate helpers, and class-specific files.

## Risks
The callback table is broad, so missing callbacks must be matched by checks in common code. Structure layout changes affect every generation backend. The WIMM wait helper is specialized around cursor space logic and should not be generalized without auditing push semantics.

## Test signals
Compile coverage across all window backends is the first signal. Runtime signals are successful plane creation, callback dispatch, WIMM point updates, and no null callback dereferences in atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc37e.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc37e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc57e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc57e.c

## Purpose
Implements the TU102/C57E window backend, reusing most C37E synchronization and blending code while changing image, CSC, input LUT, and supported modifier behavior.

## Important APIs, types, and functions
- `wndwc57e_image_set()` writes NVC57E surface methods with format rounding mode and C57E params layout.
- `wndwc57e_csc_set()` and `wndwc57e_csc_clr()` program format conversion coefficients, with clear writing an identity matrix.
- `wndwc57e_ilut_set/clr()` program C57E ILUT controls and DMA context.
- `fixedU0_16_FP16()` converts fixed-point LUT entries to FP16-like hardware encoding.
- `wndwc57e_ilut_load()` writes a VSS header, LUT entries, and a replicated last entry for interpolation safety.
- `wndwc57e_ilut()` configures direct8/direct10 LUT mode and loader callback.
- `wndwc57e_modifiers[]` advertises block-linear 2D modifiers plus linear.
- `wndwc57e_new()` delegates construction to `wndwc37e_new_()`.

## Control flow
During LUT atomic checking, common code calls `wndwc57e_ilut()` to describe the LUT buffer format; later flush uploads entries with `wndwc57e_ilut_load()` and points hardware at the buffer. Image programming follows the same high-level sequence as C37E but uses C57E class fields and omits explicit color-space/CSC fields from params. CSC clear actively restores identity coefficients.

## State and persistence
Persistent hardware state includes C57E image surface description, ILUT DMA/offset/control, CSC coefficients, and common semaphore/notifier/blend/update state inherited from C37E callbacks. Modifier exposure is a global static list.

## Dependencies and integration points
Depends on `wndw.h`, `atom.h`, DRM atomic helper, Nouveau BO, `nvif/pushc37b.h`, and `clc57e.h`. It is selected for TU102 display window classes and contributes format modifiers to Nouveau display setup.

## Risks
The fixed-to-FP16 conversion is compact and sensitive to zero/normalization behavior. LUT buffer sizing includes a VSS header and extra terminal entry; size mismatches would cause incorrect colors or memory overwrites. The image params no longer include some C37E fields, so common state must not assume identical class programming.

## Test signals
TU102 plane flips, identity and non-identity LUTs, CTM set/clear, block-linear modifiers at all listed heights, and FP16/XRGB2101010 formats should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc57e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc67e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc67e.c

## Purpose
Implements the GA102/C67E window backend. It is a small variant of the C57E backend with adjusted image storage programming.

## Important APIs, types, and functions
- `wndwc67e_image_set()` writes NVC57E-compatible methods but omits the `MEMORY_LAYOUT` field from `SET_STORAGE`.
- `static const struct nv50_wndw_func wndwc67e` reuses C37E semaphore/notifier/blend/update and C57E ILUT/CSC callbacks.
- `wndwc67e_new()` delegates to `wndwc37e_new_()`.

## Control flow
Common window code computes the same `nv50_wndw_atom` image, LUT, CSC, blend, and point state. This backend emits the GA102-compatible image method sequence, then shared callbacks handle the rest.

## State and persistence
No private state exists beyond the common window object. Hardware surface, LUT, CSC, blend, notifier, and semaphore state persist in the display channel after emitted.

## Dependencies and integration points
Uses `wndw.h`, `atom.h`, `nvif/pushc37b.h`, and `clc57e.h`. It is selected for `GA102_DISP_WINDOW_CHANNEL_DMA`.

## Risks
Because the implementation uses C57E class macros, it assumes GA102's method layout is compatible except for storage fields. Advertising inherited format/modifier behavior must remain aligned with GA102 layout restrictions enforced in `wndw.c`.

## Test signals
GA102 primary/overlay flips in linear and block-linear layouts, ILUT/CSC updates, and move-only WIMM commits are the important checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc67e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwca7e.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwca7e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/gv100_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/gv100_fence.c

## Purpose
Provides GV100-era Nouveau fence emit and sync operations using NVC36F semaphore methods, extending the NV84 fence infrastructure.

## Important APIs, types, and functions
- `gv100_fence_emit32()` releases a 32-bit sequence to a memory semaphore, emits a system membar, triggers a non-stall interrupt, and kicks the channel.
- `gv100_fence_sync32()` waits with `ACQ_CIRC_GEQ` against a 32-bit memory semaphore and kicks the channel.
- `gv100_fence_context_new()` creates the base NV84 fence channel context and overrides `.emit32`/`.sync32`.
- `gv100_fence_create()` creates the base fence private object and overrides `.context_new`.

## Control flow
Driver initialization calls `gv100_fence_create()`, which delegates to `nv84_fence_create()` and installs a GV100 context factory. Each channel context is then created through NV84 code and patched with GV100 semaphore operations. Fence emission writes address and payload, executes a release with WFI and 32-bit payload size, performs a system memory barrier, emits a non-stall interrupt, and kicks. Sync writes address/payload and executes an acquire greater-or-equal operation with TSG switching enabled.

## State and persistence
Persistent state remains in the inherited `nv84_fence_priv` and per-channel `nv84_fence_chan`. This file changes function pointers and writes GPU semaphore state to the channel pushbuffer. Fence sequence values persist in memory until overwritten.

## Dependencies and integration points
Depends on `nouveau_drv.h`, `nouveau_dma.h`, `nouveau_fence.h`, `nv50_display.h`, `nvif/push906f.h`, and `clc36f.h`. It integrates with Nouveau channel scheduling, dma-fence signaling, and legacy NV84 fence management.

## Risks
Memory ordering is critical: removing or weakening the SYS_MEMBAR can make CPU/GPU synchronization observe stale data. Address splitting and payload size must match the allocated fence memory. Missing `NON_STALL_INTERRUPT` would delay fence completion notification.

## Test signals
GPU channel workloads should signal fences reliably under stress. Cross-channel sync tests should wait for sequence values without hangs. Useful failure signals include fence timeouts, missing interrupts, or data visibility races after fence completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/gv100_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/ch7006.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/ch7006.h

## Purpose
Defines configuration parameters for the Chrontel CH7006 external TV encoder used through Nouveau's I2C encoder framework.

## Important APIs, types, and functions
- `struct ch7006_encoder_params` describes input data format, clock mode/edge, XCM/PCM clock multipliers, sync direction/encoding, output voltage level, and active-detect source.
- Enumerations cover RGB/YCrCb bus formats, master/slave clock and sync modes, separated versus embedded sync, 1.8V/3.3V POUT, and hsync/dstart active detection.

## Control flow
This header is declarative. A board or GPU-specific encoder setup passes an instance of this struct to the encoder's `set_config` callback before modesetting.

## State and persistence
No runtime state is stored here. Values persist only in the caller-owned configuration struct and then in the CH7006 device registers programmed by the driver implementation.

## Dependencies and integration points
It integrates with `encoder_i2c.h` through the generic `void *params` configuration callback. The comment references the CH7006 datasheet for field meanings.

## Risks
Fields are marked private/FIXME and underdocumented, so incorrect board data can produce wrong colors, clocks, or sync. Enum values must match the CH7006 driver implementation and hardware register encodings.

## Test signals
TV encoder bring-up should verify mode lock, color format, sync polarity/encoding, voltage level, and active detection on hardware using CH7006.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/ch7006.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/encoder_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/encoder_i2c.h

## Purpose
Defines Nouveau's generic wrapper for external display encoders connected over I2C, allowing GPU-specific code to call lower-level encoder drivers through a DRM encoder object.

## Important APIs, types, and functions
- `struct nouveau_i2c_encoder_funcs` contains callbacks for config, destroy, DPMS, save/restore, mode_fixup, prepare/commit, mode_set, detect, get_modes, create_resources, set_property, get_slave_funcs, and set_clock_mode.
- `struct nouveau_i2c_encoder` embeds `struct drm_encoder`, callback pointers, private data, and the backing `struct i2c_client`.
- `nouveau_i2c_encoder_init()` creates/initializes an I2C-backed encoder.
- `get_encoder_i2c_funcs()` and `nouveau_i2c_encoder_get_client()` are inline accessors.
- `struct nouveau_i2c_encoder_driver` wraps an `i2c_driver` plus `encoder_init`.
- `nouveau_i2c_encoder_destroy()` unregisters the I2C client, clears the pointer, and releases the driver module.
- Wrapper prototypes expose mode_fixup, detect, save, and restore.

## Control flow
The common DRM CRTC code calls normal DRM encoder hooks. Nouveau's upper layer wraps those calls and forwards them to `nouveau_i2c_encoder_funcs` only when the I2C encoder is selected for a connector. Driver initialization creates an I2C client and asks the encoder driver to populate function pointers and private data. Destroy unregisters the I2C client and drops the module reference.

## State and persistence
Persistent state lives in `struct nouveau_i2c_encoder`: the DRM encoder base, callback table pointer, implementation-private data, and I2C client. Device register state persists in the external encoder and is handled by save/restore/mode_set callbacks.

## Dependencies and integration points
Depends on Linux I2C and DRM CRTC/encoder headers. It is used by CH7006, SIL164, and similar dispnv04-era external encoder drivers.

## Risks
The callback surface is broad and many callbacks are optional, so wrapper code must null-check carefully. `nouveau_i2c_encoder_destroy()` assumes a live `client->dev.driver` and owner; calling it after partial teardown would be unsafe. Lifetime must balance `i2c_unregister_device()` and `module_put()`.

## Test signals
External encoder probe, mode detection, mode setting, DPMS, suspend/resume save/restore, and module unload paths are the key tests. Build coverage catches callback signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/encoder_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/sil164.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/sil164.h

## Purpose
Defines configuration parameters for the Silicon Image SIL164 external TMDS/DVI encoder.

## Important APIs, types, and functions
- `struct sil164_encoder_params` describes input clock edge, input width, single/dual-edge sampling, PLL filter mode, input skew, and dual-link skew.
- Enumerations represent falling/rising edge, 12/24-bit bus width, single/dual-edge input, and PLL filter on/off.

## Control flow
This header has no executable flow. Board-specific code passes the struct through the generic I2C encoder `set_config` callback.

## State and persistence
No software state is defined. The values are configuration inputs for the SIL164 driver, which persists them in encoder registers during modeset/configuration.

## Dependencies and integration points
Integrates with `encoder_i2c.h` through `void *params` and with external DVI encoder setup paths.

## Risks
Skew fields have limited ranges `[-4, 3]`; callers must validate before programming. Wrong edge/width/dual-edge settings can produce no link or corrupted pixels.

## Test signals
Hardware tests should verify DVI link lock, pixel correctness, skew tolerance, single/dual-link behavior where applicable, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/sil164.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/acr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/acr.h

## Purpose
Defines firmware data structures for NVIDIA ACR/WPR and light-secure falcon boot metadata parsed by Nouveau's firmware loader.

## Important APIs, types, and functions
- WPR headers: `struct wpr_header`, `wpr_header_v1`, `wpr_generic_header`, and `wpr_header_v2` with status and identifier constants.
- Signature and LSB headers: `struct lsf_signature`, `lsf_signature_v1`, `lsb_header_tail`, `lsb_header`, `lsb_header_v1`, and the large `lsb_header_v2` with signature, encryption, manifest, and FMC fields.
- ACR descriptors: `struct flcn_acr_desc` and `flcn_acr_desc_v1` describe WPR regions, region permissions, ucode blob, and VPR/HDCP policy.
- Dump prototypes expose structured debug output for each major format.

## Control flow
This header is declarative. Parser/dump implementations use the struct definitions to interpret binary firmware blobs and WPR contents, branching on versioned headers and generic header IDs.

## State and persistence
No live driver state is stored. The structures mirror persistent firmware blob layouts and WPR metadata consumed during secure falcon bootstrap.

## Dependencies and integration points
Uses `u8/u16/u32/u64` kernel types and `struct nvkm_subdev` for dump routines. It integrates with Nouveau's `nvfw` parsing code, ACR bootstrap, PMU/SEC2 command paths, and secure firmware loading for falcons.

## Risks
Binary layout compatibility is critical; missing packing/alignment on fields with `u64 __aligned(8)` or nested signature blobs can break parsing. Versioned formats have many similar fields, increasing copy/paste and wrong-version risks. Security-sensitive fields include signatures, dependency maps, encryption IVs, WPR permissions, and HDCP/VPR policy.

## Test signals
Firmware load should parse and dump expected WPR/LSB/ACR versions on supported GPUs. Negative tests should reject invalid status, signature, size, or offset fields. Secure boot failures usually surface as ACR validation or falcon bootstrap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/acr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/flcn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/flcn.h

## Purpose
Defines generic falcon bootloader and loader configuration descriptors used when loading NVIDIA falcon microcode.

## Important APIs, types, and functions
- `struct loader_config` and packed `loader_config_v1` describe DMA indexes, code/data/overlay DMA bases, sizes, entry points, and arguments.
- `struct flcn_bl_dmem_desc`, packed `flcn_bl_dmem_desc_v1`, and packed `flcn_bl_dmem_desc_v2` describe bootloader DMEM layout, signatures, secure/non-secure code regions, data regions, and optional argc/argv.
- Dump prototypes exist for loader and bootloader descriptor versions.

## Control flow
No executable flow is present. Firmware loader code selects the descriptor version required by the target falcon/firmware image, fills or parses it, and optionally dumps it for diagnostics.

## State and persistence
The structs represent transient DMEM descriptors and persistent firmware blob layout. No driver state is declared here.

## Dependencies and integration points
Includes `core/os.h` and forward declares `struct nvkm_subdev`. It is consumed by NVKM falcon firmware bootstrap code and works with the ACR descriptors in `acr.h`.

## Risks
Packed 64-bit descriptor versions must match firmware ABI exactly. Confusing 32-bit and 64-bit DMA base variants can boot from wrong addresses. Secure and non-secure code offsets/sizes are security-sensitive.

## Test signals
Falcon boot on GPUs using each descriptor version, debug dumps, and failure injection for bad code/data sizes are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/flcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/fw.h

## Purpose
Declares common NVIDIA firmware binary and bootloader descriptor headers plus parser entry points.

## Important APIs, types, and functions
- `struct nvfw_bin_hdr` contains binary magic/version, size, header offset, and data offset.
- `nvfw_bin_hdr()` returns a parsed binary header from a blob.
- `struct nvfw_bl_desc` contains descriptor version, size, start tag, descriptor offset, and code offsets/sizes.
- `nvfw_bl_desc()` returns a parsed bootloader descriptor.

## Control flow
The header has no inline control flow. Implementations parse a raw firmware pointer, validate basic layout/magic/version, and return typed header pointers or failure.

## State and persistence
No state is stored. The structures mirror firmware blob metadata.

## Dependencies and integration points
Forward declares `struct nvkm_subdev` for parser diagnostics. It is a foundational include for firmware-specific parsers in `nvfw`.

## Risks
Offset and size fields gate all subsequent parsing; insufficient validation risks out-of-bounds reads or loading wrong microcode sections. Version handling must remain compatible with firmware files shipped by linux-firmware.

## Test signals
Parsing known firmware blobs, rejecting truncated/corrupt blobs, and booting falcon firmware that depends on `nvfw_bl_desc` are the useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/hs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/hs.h

## Purpose
Defines high-secure firmware headers and load headers for Nouveau's secure falcon firmware parsing.

## Important APIs, types, and functions
- `struct nvfw_hs_header` and `nvfw_hs_header()` describe the base HS header: signature, patch locations, metadata, header offset, and app version.
- `struct nvfw_hs_header_v2` and parser add patch signature, num_sig, fuse version, engine id, ucode id, and dependency map.
- `struct nvfw_hs_load_header` and `nvfw_hs_load_header_v2` describe non-secure/secure code offsets and sizes, data DMA base, code entry point, and app code/data offsets.

## Control flow
No executable logic is included. Parser implementations choose the correct versioned struct and return typed pointers into firmware data.

## State and persistence
No state is stored. These structs represent firmware metadata used during secure code loading and verification.

## Dependencies and integration points
Forward declares `struct nvkm_subdev`. It integrates with falcon boot, ACR, and secure firmware loading code.

## Risks
Security-sensitive fields include signatures, fuse version, engine id, dependency map, and secure code offsets. Misparsing can either reject valid firmware or load unauthenticated/wrong code.

## Test signals
Known-good HS firmware should parse and boot. Truncated headers, bad offsets, and invalid signature metadata should be rejected with useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/hs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/ls.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/ls.h

## Purpose
Defines light-secure firmware descriptors and high-secure bootloader wrapper headers.

## Important APIs, types, and functions
- `struct nvfw_ls_desc_head` captures common descriptor metadata, date, bootloader offsets, app offsets, and resident code/data regions.
- `struct nvfw_ls_desc`, `nvfw_ls_desc_v1`, and `nvfw_ls_desc_v2` add overlay counts, overlay start/size arrays, compression, and secure bootloader flag variants.
- Parser prototypes return typed descriptors from a firmware blob.
- `struct nvfw_ls_hsbl_bin_hdr` and `nvfw_ls_hsbl_hdr` describe HS bootloader binary/header metadata and signatures.

## Control flow
The header is declarative. Firmware parsing code selects a descriptor version, reads overlay and app layout, and uses HSBL headers when a light-secure image is wrapped by a high-secure bootloader.

## State and persistence
No live state exists. Descriptors mirror persistent firmware metadata and are used transiently during firmware load.

## Dependencies and integration points
Includes `core/os.h` and forward declares `struct nvkm_subdev`. It integrates with `fw.h`, `flcn.h`, and ACR/LS falcon loaders.

## Risks
The `load_ovl[64]` arrays and overlay counts must be bounds-checked by parsers. Descriptor versions differ subtly, especially around secure bootloader and IMEM/DMEM overlay counts. Incorrect resident region offsets can break falcon boot.

## Test signals
Firmware parsing for LS descriptor versions 0/1/2, compressed and overlay-heavy images, and HSBL-wrapped images should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/ls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/pmu.h

## Purpose
Defines PMU command and message structures for Nouveau firmware interactions, especially ACR WPR setup and falcon bootstrap through the PMU.

## Important APIs, types, and functions
- `struct nv_pmu_args` stores queue indexes and offsets/sizes for PMU command/message queues.
- Unit IDs include `NV_PMU_UNIT_INIT` and `NV_PMU_UNIT_ACR`.
- `struct nv_pmu_init_msg` reports PMU init, queue IDs, queue indexes, offsets, and sizes.
- `struct nv_pmu_acr_cmd/msg` are generic ACR command/message headers.
- Specific ACR payloads include init WPR region, bootstrap single falcon, and bootstrap multiple falcons command/message structs.
- Flag constants select reset yes/no for bootstrap operations.

## Control flow
This header defines the wire format. Runtime PMU code sends a command with the unit and command type, then receives the matching message carrying error/status. ACR flows initialize the WPR region and then bootstrap one or more falcons, optionally resetting them.

## State and persistence
No C state is kept. Queue descriptors and command/message payloads mirror firmware-managed PMU queue state. WPR and falcon boot state persists in firmware/hardware after commands complete.

## Dependencies and integration points
Used by Nouveau's PMU and ACR code to communicate with PMU firmware. It complements `sec2.h`, which provides similar ACR bootstrap structures through SEC2 on newer GPUs.

## Risks
Command IDs, units, and flags must match firmware ABI. Queue offset/size parsing errors can corrupt command/message queues. Bootstrapping multiple falcons has bitmask/status coupling that must be decoded correctly by callers.

## Test signals
PMU init queue discovery, WPR setup, single and multiple falcon bootstrap, reset/no-reset variants, and error status handling should be covered on PMU-ACR GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/sec2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/sec2.h

## Purpose
Defines SEC2 command/message structures for initialization, unload, and ACR falcon bootstrap in Nouveau firmware flows.

## Important APIs, types, and functions
- `struct nv_sec2_args` stores command/message queue indexes.
- Unit IDs cover init, unload, and ACR for v1 and v2 firmware ABIs.
- `struct nv_sec2_init_msg` and `nv_sec2_init_msg_v1` report initialization and queue location/size metadata.
- `struct nv_sec2_acr_cmd/msg` are generic ACR headers.
- `struct nv_sec2_acr_bootstrap_falcon_cmd/msg` and `_v1` define falcon id, flags, and error/status fields for bootstrap.

## Control flow
Runtime SEC2 code receives an init message to discover queue indexes, then sends ACR bootstrap commands to SEC2 firmware. Newer v2 unit IDs and v1 bootstrap payloads support ABI variants.

## State and persistence
No local state is declared. The structs represent firmware queue payloads; resulting falcon boot and SEC2 state persists in firmware/hardware.

## Dependencies and integration points
Used by Nouveau SEC2 and ACR implementations. It is the SEC2 counterpart to PMU ACR command definitions.

## Risks
ABI version mismatches between unit IDs and payload layouts can make firmware ignore commands or report misleading errors. Reset flags affect falcon lifecycle and must be chosen carefully during resume or multi-falcon boot.

## Test signals
SEC2 firmware init, queue discovery, bootstrap success/failure statuses, v1/v2 unit handling, and unload paths are key runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/sec2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl0039.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl0039.h

## Purpose
Defines method offsets and fields for the legacy NV039 memory-to-memory format class.

## Important APIs, types, and functions
- Methods include `NV039_SET_OBJECT`, `NO_OPERATION`, context DMA notifies/buffer in/buffer out, input/output offsets and pitches, line length/count, format, and buffer notify.
- Field definitions cover input/output format ranges and notify modes.

## Control flow
This header is pure macro data. Pushbuffer code emits these method offsets and values to configure and run class operations.

## State and persistence
No software state is stored. Hardware object state persists in the GPU channel until changed.

## Dependencies and integration points
Used by low-level Nouveau class programming for legacy DMA copy/format operations.

## Risks
Method offsets are ABI constants. Any incorrect value corrupts pushbuffer programming. Notify mode selection affects synchronization semantics.

## Test signals
Build use and runtime legacy DMA copy/format operations with notifications validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl0039.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006c.h

## Purpose
Defines DMA push channel get/put registers and method descriptor bitfields for NV06C-style channels.

## Important APIs, types, and functions
- `NV06C_PUT`/`GET` and pointer fields.
- Method descriptor fields: address, subchannel, count, opcode, and data.
- Opcodes include incrementing method, non-incrementing method, and jump with offset.

## Control flow
No code executes here. Pushbuffer builders use the bitfield macros to encode DMA commands and channel pointer updates.

## State and persistence
No C state exists. PUT/GET represent channel state in hardware memory/registers.

## Dependencies and integration points
Integrated into low-level NVIF/Nouveau pushbuffer encoding for old DMA classes.

## Risks
Wrong opcode/count/address fields cause GPU method decode failures or hangs. Pointer fields are word-aligned (`31:2`) and require proper alignment.

## Test signals
Legacy pushbuffer execution, jump handling, and GET/PUT progress are the runtime indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006e.h

## Purpose
Defines minimal NV06E channel methods for object selection and reference tracking.

## Important APIs, types, and functions
- `NV06E_SET_OBJECT`.
- `NV06E_REFERENCE`.
- `NV06E_SET_REFERENCE`.

## Control flow
Declarative only. Channel code writes these methods to select an object or manage reference values.

## State and persistence
No software state. Hardware reference/object state persists in the channel.

## Dependencies and integration points
Used by old Nouveau channel/object management code.

## Risks
Reference handling is synchronization-sensitive; wrong method offsets can break fence-like progress tracking.

## Test signals
Legacy channel object selection and reference updates provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl006e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl176e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl176e.h

## Purpose
Defines semaphore methods for NV176E-style DMA objects.

## Important APIs, types, and functions
- `NV176E_SET_OBJECT`.
- `NV176E_SET_CONTEXT_DMA_SEMAPHORE`.
- `NV176E_SEMAPHORE_OFFSET`.
- `NV176E_SEMAPHORE_ACQUIRE`.
- `NV176E_SEMAPHORE_RELEASE`.

## Control flow
Pure macro definitions. Pushbuffer code binds a semaphore context, sets an offset, and emits acquire/release payloads.

## State and persistence
No C state. Bound semaphore context and current offset/payload state persist in the hardware object.

## Dependencies and integration points
Used by Nouveau synchronization paths for older hardware classes.

## Risks
Semaphore offsets and context DMA handles must point at valid memory. Acquire/release ordering impacts GPU/CPU synchronization.

## Test signals
Semaphore-based waits/releases and fence progress on affected classes are the key runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl176e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl206e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl206e.h

## Purpose
Defines second-word DMA opcode fields for long jumps and calls in NV206E-style DMA pushbuffers.

## Important APIs, types, and functions
- `NV206E_DMA_OPCODE2` with `NONE`, `JUMP_LONG`, and `CALL` values.
- `NV206E_DMA_JUMP_LONG_OFFSET`.
- `NV206E_DMA_CALL_OFFSET`.

## Control flow
No execution in the header. Pushbuffer construction uses these macros to encode control-flow commands.

## State and persistence
No software state. GPU command processor state changes when it decodes long jump/call commands.

## Dependencies and integration points
Used by low-level pushbuffer management where command streams need non-linear control flow.

## Risks
Offsets are aligned to bits `31:2`; invalid targets can hang command processing. CALL stack behavior depends on hardware class support.

## Test signals
Pushbuffer long jump and call/return paths on supported GPUs validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl206e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl502d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl502d.h

## Purpose
Defines the NV50 2D engine class method offsets, fields, and format values used for blits, solid fills, CPU-to-pixel uploads, clipping, ROPs, semaphores, and synchronization.

## Important APIs, types, and functions
- Object/context methods: `NV502D_SET_OBJECT`, wait idle, destination/source/semaphore context DMA.
- Surface methods: destination/source format, memory layout, pitch, dimensions, and 64-bit offsets.
- Operation methods: clip enable, ROP, operation mode, monochrome pattern, solid primitive mode/color/points, and CPU pixel upload controls.
- Synchronization methods include semaphore offset/acquire/release and notify-related fields later in the file.
- Format constants cover common ARGB/XRGB/BGR/RGB565/index/luminance/floating formats.

## Control flow
The file is declarative. 2D acceleration code emits sequences of these methods to bind surfaces, select operation type, and trigger drawing or copy operations.

## State and persistence
No C state exists. Programmed 2D object state persists in the GPU channel between method writes.

## Dependencies and integration points
Used by Nouveau's 2D acceleration and copy paths. The format constants must align with DRM/Nouveau format translation.

## Risks
The header is large and ABI-sensitive. Wrong format, pitch, layout, or offset definitions cause memory corruption or incorrect rendering. Semaphore/notify definitions affect synchronization correctness.

## Test signals
2D solid fills, blits, CPU uploads, ROP/blend variants, tiled and linear surfaces, and semaphore waits/releases should validate this class definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl502d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl5039.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl5039.h

## Purpose
Defines NV5039 memory-to-memory format class methods for tiled/linear source and destination copies.

## Important APIs, types, and functions
- Context DMA methods for notify, input buffer, and output buffer.
- Source and destination memory layout, block size width/height/depth, dimensions, layer, origin, high/low offsets.
- Pitch, line length/count, format, and buffer notify methods.
- Format fields cover input/output format packing.

## Control flow
Declarative only. Copy/format code programs source and destination layout first, then offsets/pitches/line counts, then triggers buffer notify or operation methods.

## State and persistence
No software state. Hardware copy object state persists in the channel.

## Dependencies and integration points
Used by Nouveau memory copy/format paths that need block-linear layout awareness.

## Risks
Block-size fields must match actual tiling. Misprogrammed offsets or layouts can corrupt VRAM. Notify behavior affects completion signaling.

## Test signals
Linear-to-linear, tiled-to-linear, and tiled-to-tiled copies with notifications and varied block heights validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl5039.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507a.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507a.h

## Purpose
Defines NV507A cursor channel methods for free-count, update interlock, and cursor hotspot output point.

## Important APIs, types, and functions
- `NV507A_FREE_COUNT`.
- `NV507A_UPDATE` and `INTERLOCK_WITH_CORE` field values.
- `NV507A_SET_CURSOR_HOT_SPOT_POINT_OUT` with X/Y fields.

## Control flow
No executable flow. Cursor channel code emits hotspot and update methods, optionally interlocking with core updates.

## State and persistence
No C state. Cursor hotspot and update state persist in the cursor channel.

## Dependencies and integration points
Used by Nouveau cursor display code and by immediate push space logic referenced from `wndw.h`.

## Risks
Hotspot X/Y fields are bounded bitfields; overflow truncation can place the cursor incorrectly. Interlock choice affects cursor/core synchronization.

## Test signals
Cursor movement and hotspot changes, especially during modesets/core updates, validate this definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507c.h

## Purpose
Defines NV507C base channel notification layout, DMA command encoding, present control, notifier/semaphore methods, context DMA, image surface methods, and update/interlock methods for base display windows.

## Important APIs, types, and functions
- Notifier layout: `NV_DISP_BASE_NOTIFIER_1_*` presentation count and status.
- DMA opcodes and fields: method, non-incrementing method, jump, get, set reference.
- Presentation and sync methods: `NV507C_SET_PRESENT_CONTROL`, notifier/semaphore contexts, offsets, acquire/release, and awakener behavior.
- Surface methods: context DMA ISO, composition control, surface offset/size/storage/params, color spaces and formats.
- Update/interlock methods for display commit synchronization.

## Control flow
Declarative only. Base window and overlay code uses these macros in `PUSH_MTHD()` calls to build display method streams.

## State and persistence
No C state. Programmed base channel state persists in hardware; notifier memory stores presentation status/count.

## Dependencies and integration points
Used heavily by `base507c_*`, overlay, cursor, and window code in `dispnv50`.

## Risks
These definitions are central to atomic display commits. Wrong status values break notifier waits; wrong surface fields break scanout; wrong interlock bits cause update races.

## Test signals
Atomic modesets/flips, notifier begun/finished waits, semaphore synchronization, and base plane scanout across formats are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507d.h

## Purpose
Defines the NV507D display core channel class: core notifications, DMA command encoding, update/control methods, head timing/LUT/cursor/viewport methods, and SOR/PIOR output control.

## Important APIs, types, and functions
- Core notifier fields report display completion/capability status.
- DMA command fields support method, non-incrementing method, jump, get, and reference operations.
- Core update methods include interlock flags and modeset state.
- Head methods cover context DMAs, offset, format, size, storage, parameters, cursor controls, viewport points, and LUT-related programming.
- Output methods include `SOR_SET_CONTROL(a)` and `PIOR_SET_CONTROL(a)` owner, sub-owner, protocol, sync polarity, and pixel-depth fields.

## Control flow
No code executes here. Core display code emits these method macros during atomic modesets, output assignment, cursor updates, and LUT programming.

## State and persistence
No local state. Hardware core, head, and output state persists in display core until reprogrammed. Notifier memory persists status/capability words.

## Dependencies and integration points
Used by `core507d`, SOR/PIOR backends, head backends, and base/overlay update paths.

## Risks
The core class spans much of display hardware. Incorrect field values can misroute heads, program invalid timings, corrupt LUT/cursor state, or break notifier waits. Output protocol and ownership fields are especially modeset-critical.

## Test signals
Full modeset matrices across heads/outputs, cursor, LUT, viewport, interlock, and notifier status are required to validate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507e.h

## Purpose
Defines NV507E overlay channel notification and surface programming methods.

## Important APIs, types, and functions
- Overlay notification status/count fields.
- Present control with begin mode and minimum present interval.
- Context DMA ISO, composition control, surface offset, size, storage, and params methods.
- Format constants include packed YUV, RGB565/1555/8888/2101010, and color-space values.

## Control flow
Declarative only. Overlay backends emit these macros to configure and present overlay images.

## State and persistence
No C state. Overlay hardware state persists until cleared or updated; notification memory tracks presentation progress.

## Dependencies and integration points
Used by older overlay implementations and common `nv50_wndw` image format mapping.

## Risks
Format/color-space mapping must match DRM format handling. Present interval or notifier status mismatch can break atomic flip completion.

## Test signals
Overlay enable/disable, YUV and RGB formats, notification waits, and present interval changes validate the class header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl507e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl826f.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl826f.h

## Purpose
Defines NV826F channel/control methods, mainly reference and semaphore operations for a FIFO/channel class.

## Important APIs, types, and functions
- Methods include set object/reference, semaphore context DMA, offset, acquire, release, and release-wfi controls.
- Field macros define reference value and semaphore payloads.

## Control flow
Declarative only. Channel synchronization code emits these methods to wait on or release semaphores.

## State and persistence
No C state. Semaphore context, offset, and payload state persist in the channel object.

## Dependencies and integration points
Used by Nouveau push/fence synchronization on classes that expose NV826F semantics.

## Risks
Semaphore acquire/release programming is ordering-sensitive. Wrong WFI setting can signal before prior work is visible.

## Test signals
Fence waits/releases and cross-channel synchronization on NV82-class hardware are the relevant runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl826f.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827c.h

## Purpose
Defines NV827C base display channel methods, an evolution of NV507C with base notifier and surface programming fields.

## Important APIs, types, and functions
- Base notifier layout and status values.
- Present control, notifier/semaphore setup, context DMA ISO, composition, surface offset/size/storage/params, and update methods.
- Format and color-space constants mirror the supported base/overlay scanout formats for that generation.

## Control flow
No executable code. Base channel implementations use the macros to emit method streams for scanout and synchronization.

## State and persistence
No C state. Hardware channel and notifier memory state persist between updates.

## Dependencies and integration points
Used by Nouveau display base/overlay code for NV82-era classes and by notification wait helpers.

## Risks
Notifier status values and surface field layouts must stay synchronized with helper code. Pitch/block-linear fields are alignment-sensitive.

## Test signals
Base plane scanout, notifier waits, semaphore synchronization, and format/layout coverage validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827d.h

## Purpose
Defines NV827D display core channel methods for head image/cursor/viewport programming and output control.

## Important APIs, types, and functions
- Core notifier fields and update/interlock controls.
- Head methods for context DMA ISO, cursor control/offset/context, viewport point, and scanout params.
- SOR and PIOR control fields for owner, sub-owner, protocol, sync polarity, and pixel depth.

## Control flow
Declarative. Display core backends emit the methods during modeset, cursor, and output resource programming.

## State and persistence
No local state. Display core/head/output state persists in hardware and notifier memory.

## Dependencies and integration points
Used by NV827D-era core/head/output implementations and by shared field definitions referenced by SOR/PIOR code.

## Risks
Output protocol and cursor ownership bits are hardware-critical. Wrong field masks can cause blank displays or cursor corruption.

## Test signals
Modesets on all supported output protocols, cursor format/size/hotspot tests, and interlock/notifier validation are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827e.h

## Purpose
Defines NV827E overlay channel notification and surface methods.

## Important APIs, types, and functions
- `NV_DISP_NOTIFICATION_1_*` timestamp, present count, and status fields.
- `NV827E_SET_PRESENT_CONTROL`, ISO context DMA, composition control, surface offset/size/storage/params.
- Format constants include packed YUV and selected RGB formats; color-space constants include RGB, YUV 601, and YUV 709.

## Control flow
Declarative only. Overlay code emits these macros to present images and track notification status.

## State and persistence
No C state. Overlay method state and notification memory persist until reprogrammed.

## Dependencies and integration points
Used by overlay backends such as the 827E/907E family and shared notification helpers.

## Risks
Status constants drive wait logic; wrong values can hang or prematurely complete flips. Surface offset and pitch fields have alignment requirements.

## Test signals
Overlay atomic flips, notification begun/finished waits, YUV/RGB output, and storage layout changes validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl827e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl837d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl837d.h

## Purpose
Defines NV837D SOR and PIOR output-control fields for owner, sub-owner, protocol, sync polarity, DE polarity, and pixel depth.

## Important APIs, types, and functions
- `NV837D_SOR_SET_CONTROL(a)` and field constants for LVDS, TMDS, DDI/custom protocols and bpp/depth modes.
- `NV837D_PIOR_SET_CONTROL(a)` and field constants for external TMDS/TV encoder protocols and depth modes.

## Control flow
No code executes. SOR/PIOR backends use these field definitions when constructing control words.

## State and persistence
No C state. Programmed output-resource state persists in display hardware.

## Dependencies and integration points
Included by `sor507d.c` and `pior507d.c` for pixel-depth field definitions alongside NV507D method offsets.

## Risks
Protocol/depth values must match the actual output resource. Incorrect owner/sub-owner or protocol fields can route a head incorrectly or blank an output.

## Test signals
SOR and PIOR modesets across DVI/HDMI/LVDS/TV paths, depth changes, and polarity-sensitive modes are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl837d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl887d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl887d.h

## Purpose
Defines NV887D SOR output-control fields, extending the NV837D-style protocol list with explicit DisplayPort A/B protocol values.

## Important APIs, types, and functions
- `NV887D_SOR_SET_CONTROL(a)` method offset.
- Owner/sub-owner fields for head routing.
- Protocol constants for LVDS, TMDS, DDI, `DP_A`, `DP_B`, and custom.
- Hsync/vsync/DE polarity and pixel-depth constants.

## Control flow
This is a declarative class header. Display output code uses these macros to build SOR control words.

## State and persistence
No software state. Hardware SOR control state persists until the next modeset/update.

## Dependencies and integration points
Used by NV887D-era display output backends and code that needs explicit DP link selection.

## Risks
DP_A/DP_B protocol selection must match link routing. Wrong owner or protocol values can light the wrong link or fail link training. Pixel-depth constants must be consistent with head configuration.

## Test signals
DisplayPort A/B modesets, TMDS/LVDS fallback paths, bpc/depth changes, and polarity checks validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl887d.h -->
