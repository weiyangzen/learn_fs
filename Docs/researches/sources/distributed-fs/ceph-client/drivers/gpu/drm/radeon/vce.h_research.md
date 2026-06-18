# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce.h

## Purpose

`vce.h` is the private Radeon VCE header for generation-specific media clock-gating control. It forward declares `struct radeon_device` and exposes MGC clock-gating toggles for VCE 1.0 and VCE 2.0 implementations.

## Important APIs, Types, and Functions

- `vce_v1_0_enable_mgcg(struct radeon_device *rdev, bool enable)`.
- `vce_v2_0_enable_mgcg(struct radeon_device *rdev, bool enable)`.

## Control Flow

The header has no runtime flow. Callers such as Trinity DPM include it to turn VCE medium-grain clock gating off while encoding clocks are active and on again when VCE clocks are disabled.

## State and Persistence Behavior

No state is stored in the header. Implementations persist changes in VCE hardware clock-gating registers.

## Dependencies and Integration Points

- Consumed by `trinity_dpm.c`, `vce_v1_0.c`, and `vce_v2_0.c`.
- Requires callers to include a definition for `bool` and the Radeon device type through surrounding includes.

## Risks and Edge Cases

- This header exposes only clock-gating toggles, so other VCE generation functions must be declared elsewhere or through ASIC callback tables.
- Calling the wrong generation function for an ASIC can write incompatible registers.

## Test Signals

- Build coverage should ensure VCE MGC clock-gating prototypes match both implementation files and all callers.
- Runtime clock tests should verify VCE gating changes match the selected ASIC generation.
