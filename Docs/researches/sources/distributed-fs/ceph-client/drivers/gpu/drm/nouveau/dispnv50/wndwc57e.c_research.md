
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
