# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v6_0.h

## Purpose

`gfx_v6_0.h` is the public local header for the GFX6 AMDGPU IP block. It declares the single exported IP block descriptor implemented by `gfx_v6_0.c`, allowing the broader AMDGPU device-discovery and IP-block assembly code to reference the GFX6 implementation without exposing the many private helper functions used inside the C file.

## Important APIs, Types, And Functions

- Header guard: `__GFX_V6_0_H__`.
- Exported declaration: `extern const struct amdgpu_ip_block_version gfx_v6_0_ip_block;`.
- The declared type, `struct amdgpu_ip_block_version`, is defined elsewhere in AMDGPU core headers. In the C implementation it identifies the block as `AMD_IP_BLOCK_TYPE_GFX`, version 6.0.0, and points at the GFX6 lifecycle callback table.

There are no inline helpers, macros, structs, or private declarations in this header. It intentionally keeps the external surface small.

## Control Flow

This header has no runtime control flow. Its declaration participates at compile and link time: code that includes this header can place `gfx_v6_0_ip_block` into an ASIC-specific IP block list. At runtime, that block descriptor leads the AMDGPU IP framework to call the implementation's early init, software init, hardware init, suspend/resume, idle, and power-management callbacks.

## State And Persistence Behavior

The header owns no state and causes no persistence. State is attached to the external object declared here and to the `amdgpu_device` fields mutated by the implementation. Because the object is declared `const`, consumers should treat it as immutable descriptor data.

## Dependencies And Integration Points

The header assumes any including translation unit already has visibility for `struct amdgpu_ip_block_version`, normally through AMDGPU core headers. Its only integration point is the symbol `gfx_v6_0_ip_block`, which is defined in `gfx_v6_0.c` and consumed by GPU family setup code that chooses the correct IP blocks for Southern Islands / GFX6 devices.

## Risks And Edge Cases

- Include-order sensitivity is possible if a consumer includes this header before a declaration of `struct amdgpu_ip_block_version`; the header does not forward declare the struct itself.
- Any rename or signature change of `gfx_v6_0_ip_block` must be coordinated with all ASIC block-list users and the C definition.
- The minimal header is beneficial for encapsulation, but it means tests or other code cannot call private GFX6 helper functions directly without adding new declarations.

## Test Signals

Build and link success are the primary test signals for this header. Runtime validation is indirect: if the symbol is wired correctly, GFX6 devices should reach the `gfx_v6_0` IP callbacks during AMDGPU initialization, firmware loading, ring setup, and suspend/resume flows.
