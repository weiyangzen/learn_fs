# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.c

## Purpose
`mmio.c` is the front door for guest MMIO and GGTT MMIO emulation. It translates guest physical addresses into BAR0 offsets, validates access size/alignment/ranges, dispatches GGTT accesses to GTT emulation, dispatches tracked MMIO accesses to `handlers.c`, and owns allocation/reset/free of each vGPU virtual MMIO image.

## Important APIs, Types, And Functions
Public functions are `intel_vgpu_gpa_to_mmio_offset`, `intel_vgpu_emulate_mmio_read`, `intel_vgpu_emulate_mmio_write`, `intel_vgpu_reset_mmio`, `intel_vgpu_init_mmio`, and `intel_vgpu_clean_mmio`. Private helpers include MMIO/GTT range checks and `failsafe_emulate_mmio_rw`.

## Control Flow
Read/write paths check failsafe mode, lock `vgpu_lock`, compute offset, validate widths, route GGTT offsets to `intel_vgpu_emulate_ggtt_mmio_read/write`, route MMIO offsets to `intel_vgpu_mmio_reg_rw`, and mark successful MMIOs accessed. Invalid non-MMIO ranges fall back to guest GPA read/write with warnings. Reset copies firmware MMIO defaults into `vgpu->mmio.vreg` and adjusts GT, GuC, and Broxton power/PHY status bits; non-DMLR reset copies only the engine-related prefix.

## State And Persistence
`vgpu->mmio.vreg` is a `vzalloc` buffer sized by `gvt->device_info.mmio_size` and seeded from `gvt->firmware.mmio`. The file also touches virtual GGTT memory in failsafe mode and depends on device info offsets/sizes.

## Dependencies And Integration Points
KVMGT calls this for BAR0. `handlers.c` supplies `intel_vgpu_mmio_reg_rw` and defaults. GTT emulation handles GGTT entries. Firmware loading supplies reset defaults.

## Risks
MMIO/GGTT/out-of-range classification and alignment checks must be exact. Failsafe bypasses semantic handlers and must remain a containment path. Platform reset defaults can drift from i915/hardware behavior.

## Test Signals
Correct BAR0 MMIO/GGTT routing, warnings on invalid access, reset defaults, Broxton status bits, 4/8-byte GGTT access, no lock inversions, and safe failsafe access after unsupported guest behavior.
