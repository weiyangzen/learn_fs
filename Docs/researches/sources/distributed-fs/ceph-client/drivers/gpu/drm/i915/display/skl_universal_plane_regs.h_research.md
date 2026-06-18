# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_universal_plane_regs.h

Purpose: defines MMIO register address macros and bit fields for SKL+ universal plane programming. It covers plane control, stride, position, size, color keying, surface base/live address, offsets, AUX distance/offset, chroma upsampling, plane color control, input/plane CSC, per-plane gamma LUTs, watermarks, DDB buffer configuration, selected-fetch registers, plane pixel normalizer, and selected platform-specific fields.

Important APIs/types/functions: address constructors include `_SKL_PLANE()`, `_SKL_PLANE_DW()`, `_MMIO_SKL_PLANE()`, `_MMIO_SKL_PLANE_DW()`, `_SEL_FETCH()`, and `_MMIO_SEL_FETCH()`. Main register macros include `PLANE_CTL`, `PLANE_STRIDE`, `PLANE_POS`, `PLANE_SIZE`, `PLANE_KEYVAL`, `PLANE_KEYMSK`, `PLANE_SURF`, `PLANE_SURFLIVE`, `PLANE_KEYMAX`, `PLANE_OFFSET`, `PLANE_CC_VAL`, `PLANE_AUX_DIST`, `PLANE_AUX_OFFSET`, `PLANE_CUS_CTL`, `PLANE_COLOR_CTL`, `PLANE_INPUT_CSC_*`, `PLANE_CSC_*`, `PLANE_WM`, `PLANE_WM_TRANS`, `PLANE_WM_SAGV`, `PLANE_WM_SAGV_TRANS`, `PLANE_NV12_BUF_CFG`, `PLANE_BUF_CFG`, `PLANE_MIN_BUF_CFG`, `SEL_FETCH_PLANE_*`, and `PLANE_PIXEL_NORMALIZE`.

Control flow: implementation files use these macros to compose register writes and reads with `intel_de_read()`, `intel_de_write()`, `intel_de_write_dsb()`, and read-modify-write helpers. `PLANE_CTL` fields encode enable, arbitration slots, format, color key mode, RGB order, YUV420 Y-plane tagging, CSC/range, compression, tiling, async flip, horizontal flip, alpha, and rotation.

State and persistence behavior: the header defines symbolic access to hardware state but owns no runtime data. Its bit definitions become persistent hardware state only when written by display commit code. Some bit positions intentionally alias across generations, so callers must gate by display version.

Dependencies and integration points: depends on `intel_display_reg_defs.h` for `_MMIO`, `_PIPE`, `_PLANE`, `_PICK`, and `REG_*` helpers. It is shared by `skl_universal_plane.c`, `skl_watermark.c`, cursor/watermark code, and color pipeline code that must address per-plane registers.

Risks: generation aliasing is the major risk. A field that is valid on one display version can mean something else on another; implementation code must preserve version checks. Plane and selective-fetch address helpers encode non-linear plane numbering and pipe ranges, so adding new planes or display versions requires careful validation against BSpec.

Test signals: build-time compile coverage, register read/write trace comparison with BSpec, hardware state dumps before and after commits, watermark verification, selected-fetch enable/disable tests, and modifier-specific plane programming tests all exercise this header.
