# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.h

## Purpose

`si.h` is the small private Southern Islands interface shared by SI-specific Radeon implementation files and neighboring ASIC code. It forward-declares core Radeon structs and exposes a focused set of helper entry points implemented in `si.c`.

## Important APIs, Types, and Functions

- `struct radeon_device` and `struct radeon_mc` are forward declarations so callers do not need full definitions from this header alone.
- `si_mc_load_microcode(struct radeon_device *rdev)` uploads MC firmware and associated IO debug register tables.
- `si_gpu_check_soft_reset(struct radeon_device *rdev)` returns a `RADEON_RESET_*` mask based on SI busy/status registers.
- `si_vram_gtt_location(struct radeon_device *rdev, struct radeon_mc *mc)` lays out VRAM and GTT apertures with SI address-space limits.
- `si_rlc_reset(struct radeon_device *rdev)` pulses the RLC soft-reset bit.
- `si_init_uvd_internal_cg(struct radeon_device *rdev)` applies UVD internal clock-gating defaults.
- `si_get_csb_size(struct radeon_device *rdev)` and `si_get_csb_buffer(struct radeon_device *rdev, volatile u32 *buffer)` expose RLC clear-state-buffer sizing and packet generation.

## Control Flow

The header does not implement control flow; it provides cross-file linkage. `si.c` calls some of these internally and other Radeon modules can call them through direct declarations or ASIC callback tables. Typical flow is: memory setup uses `si_vram_gtt_location`, startup or DPM code invokes `si_mc_load_microcode`, reset/lockup logic checks `si_gpu_check_soft_reset`, RLC setup uses `si_rlc_reset` and CSB helpers, and UVD setup can call `si_init_uvd_internal_cg`.

## State and Persistence Behavior

All functions operate on the persistent `struct radeon_device` and, for aperture layout, `struct radeon_mc`. The header itself owns no state. Callers should expect the implementations to write persistent GPU registers and mutate `rdev` fields such as MC layout, firmware state, RLC buffers, UVD clock-gating state, and reset observations.

## Dependencies and Integration Points

- Included by `si.c` and `si_dma.c`; its declarations are also consistent with prototypes in `radeon_asic.h`.
- Depends on fixed-width `u32` being visible before or through common Radeon includes in users.
- Integrates SI reset, MC, RLC, and UVD helpers with the wider Radeon ASIC and VM/DMA code.

## Risks and Edge Cases

- The header relies on external include order for `u32`; it is private to the Radeon tree where that is normally satisfied.
- Exporting only partial SI helpers means prototype drift between this header, `radeon_asic.h`, and implementations can break builds.
- The functions have hardware side effects but no contract comments in this header, so callers must understand required initialization state from implementation context.

## Test Signals

- Build coverage should include `si.c`, `si_dma.c`, and `radeon_asic.c` to catch signature drift.
- Runtime tests should confirm callers only use these helpers after `rdev` register access, firmware pointers, RLC buffers, or MC fields are initialized as required by the implementation.
