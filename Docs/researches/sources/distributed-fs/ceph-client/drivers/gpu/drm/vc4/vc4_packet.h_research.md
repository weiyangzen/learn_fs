# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_packet.h

Purpose: Defines the VC4/V3D command-list packet opcodes, packet byte sizes, render/binning bit fields, texture descriptor fields, tiling identifiers, and texture data type enum used by the VC4 render and validation code. It is a hardware ABI header inside the driver: no executable code, but many safety checks and command emitters depend on these constants matching hardware.

Important APIs/types/functions: `enum vc4_packet` names hardware packets plus the driver-only `VC4_PACKET_GEM_HANDLES` relocation pseudo-packet. `VC4_PACKET_*_SIZE` constants feed command-list length accounting in `vc4_validate.c` and RCL allocation in `vc4_render_cl.c`. The `VC4_LOADSTORE_*`, `VC4_RENDER_CONFIG_*`, `VC4_BIN_CONFIG_*`, `VC4_TEX_P*_*`, and `enum vc4_texture_data_type` definitions describe the packed fields later accessed through `VC4_GET_FIELD()` and `VC4_SET_FIELD()`.

Control flow: None locally. The header shapes control flow elsewhere by defining packet dispatch indexes in `cmd_info[]`, RCL packet emission order, and texture relocation decoding.

State and persistence: No runtime state. The values are persistent driver/hardware ABI constants; changing them affects submitted command streams, render target validation, and texture bounds checks.

Dependencies and integration points: Includes `vc4_regs.h` for bit helpers. Used by `vc4_validate.c` to whitelist and relocate bin CL packets, by `vc4_render_cl.c` to synthesize render CL packets, and by shader/texture validation to interpret uniforms. It also indirectly couples to userspace UAPI structs whose `bits` fields are expected to contain these encodings.

Risks: A bad size constant can under-allocate or overrun validated command buffers. A bad mask/shift can validate one field while hardware interprets another. The duplicated `VC4_LOADSTORE_FULL_RES_*` block should be treated carefully during edits. `VC4_PACKET_GEM_HANDLES` is not hardware, so consumers must keep filtering it out of emitted CLs.

Test signals: Submit CL validation tests should fail invalid packets/lengths and pass legal primitive/shader/binning packets. Render tests should exercise load/store general, full-res MSAA, tiling formats, texture formats, and `VC4_SUBMIT_RCL_SURFACE_*` combinations.
