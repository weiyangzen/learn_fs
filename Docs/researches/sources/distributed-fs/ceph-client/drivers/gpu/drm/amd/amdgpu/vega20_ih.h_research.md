# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega20_ih.h

## Purpose

`vega20_ih.h` is the public declaration header for the Vega20 IH IP block implementation. It exposes the function-table object and IP-block descriptor defined by `vega20_ih.c` so other AMDGPU initialization code can reference and register the IH block.

## Important APIs, Types, And Functions

The header declares two external constants:

- `extern const struct amd_ip_funcs vega20_ih_ip_funcs;`
- `extern const struct amdgpu_ip_block_version vega20_ih_ip_block;`

It does not define local types, inline functions, register macros, or data structures. The referenced types are declared by AMDGPU core headers included by C files that include this header.

## Control Flow

There is no runtime control flow in the header. It participates in compile-time linkage:

1. A C file includes `vega20_ih.h`.
2. The compiler sees the external declarations.
3. Linkage resolves the objects to their definitions in `vega20_ih.c`.
4. Device discovery or ASIC setup code can pass `&vega20_ih_ip_block` into AMDGPU IP block registration.

## State And Persistence Behavior

The header has no mutable state and no persistence behavior. It only makes externally defined constant objects visible across translation units.

## Dependencies

The file depends on the definitions of `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` being visible to consumers. It protects itself with `__VEGA20_IH_H__` include guards and carries AMD's MIT-style license text.

## Integration Points

Primary integration is with AMDGPU discovery and SOC setup code. Repository search shows `vega20_ih_ip_block` is used by discovery code to add the Vega20 IH block, while `vega20_ih.c` includes this header to keep declarations consistent with definitions.

## Risks

- If the declarations diverge from the definitions in `vega20_ih.c`, build or link failures will occur.
- Because the header does not include the core type declarations itself, include ordering must provide `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. This is normal for internal AMDGPU headers but can surprise isolated include tests.
- The include guard name must remain unique to avoid accidental exclusion with another header.

## Test Signals

Useful signals are build-oriented:

- Compile units that include `vega20_ih.h` without duplicate symbol or incomplete type errors.
- Link succeeds with `vega20_ih.c` included in the AMDGPU build.
- Device discovery can reference `vega20_ih_ip_block` and register the block for supported ASICs.
