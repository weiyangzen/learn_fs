# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_drv.h

Purpose: central Loongson DRM header defining chip descriptors, KMS function tables, DRM object wrappers, device state, conversion helpers, prototypes, and MMIO accessors.

Important APIs/types/functions: `struct lsdc_desc`, `struct loongson_gfx_desc`, `struct lsdc_crtc_hw_ops`, `struct lsdc_crtc`, primary/cursor ops and wrappers, `struct lsdc_output`, `struct lsdc_display_pipe`, `struct lsdc_kms_funcs`, `struct lsdc_crtc_state`, `struct lsdc_gem`, `struct lsdc_device`, conversion helpers, and register read/write helpers.

Control flow: no executable flow beyond inline accessors. Core code uses descriptors to dispatch chip-specific KMS construction and hardware ops.

State and persistence: `lsdc_device` is the root runtime state for PCI, DRM, TTM, MMIO, VRAM/GTT, display pipes, GEM tracking, IRQ status, and pinned memory.

Dependencies and integration points: includes PCI, DRM connector/CRTC/encoder/file/plane/TTM, and local I2C/IRQ/GFXPLL/output/pixpll/register headers. It is included across the Loongson driver.

Risks and test signals: structure layout underpins container conversions; mismatches can corrupt memory. MMIO helpers do not lock except where callers use `reglock`. Test compile coverage, KMS init for both descriptors, concurrent I2C/register access, and TTM/GEM cleanup.
