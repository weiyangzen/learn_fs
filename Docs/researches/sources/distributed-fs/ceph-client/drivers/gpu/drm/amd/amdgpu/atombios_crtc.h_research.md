# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_crtc.h

## Purpose
This header declares the legacy ATOMBIOS CRTC, timing, display-clock, and PLL helper API.

## Important APIs, types, and functions
It declares helpers for overscan, scaler, CRTC lock/enable/blank, display power gating, DTD timing, display-engine PLL programming, DCE clock programming, pixel PLL programming, PLL preparation, and final PLL set.

## Control flow
The header is declarative. Modesetting code calls the declared functions in the order required by the legacy display pipeline: prepare PLL, program timing/scaler/overscan, enable or blank CRTC, and set PLL/clock state.

## State and persistence behavior
No state is stored in the header. Implementations mutate hardware through ATOM command tables and update `amdgpu_crtc`/clock fields.

## Dependencies
The prototypes rely on DRM CRTC/display mode types, AMDGPU device types, and `struct amdgpu_atom_ss` from ATOMBIOS headers being visible.

## Integration points
Legacy display code, encoder code, and modeset paths include this header to invoke CRTC/PLL helpers.

## Risks and edge cases
As a prototype header, the main risk is include-order or signature drift. The large `program_pll` signature is error-prone because many adjacent `u32` arguments share units-sensitive meanings.

## Test signals
Compile coverage and modeset execution through all declared helpers validate it.
