# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/navi10_sdma_pkt_open.h lines 4600-4886

## Scope

This chunk covers the final 287 lines of `navi10_sdma_pkt_open.h`. The range starts in the `SDMA_AQL_PKT_COPY_LINEAR` packet definition, covers its remaining header and payload field macros, defines the complete `SDMA_AQL_PKT_BARRIER_OR` packet layout, and closes the header guard. This is a generated-style packet-description header, so the important behavior is the binary command/AQL ABI it exposes rather than C control flow.

## Purpose

The chunk provides bitfield helpers for constructing Navi10 SDMA AQL packets. These macros let AMDGPU/KFD-side code or generated packet-building code encode 32-bit words for SDMA AQL linear copies and AQL barrier-or packets without open-coded shifts and masks. The definitions describe:

- The tail of the 16-DW `SDMA_AQL_PKT_COPY_LINEAR` packet, including header control fields, return address, copy count, source/destination swizzle selectors, source/destination addresses, reserved words, and completion signal address.
- The full 16-DW `SDMA_AQL_PKT_BARRIER_OR` packet, including common AQL header fields, up to five dependent signal addresses, reserved words, and completion signal address.
- The end of the `__NAVI10_SDMA_PKT_OPEN_H_` include guard.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime callbacks in this range. The public surface is a large set of `#define` constants and packing macros. Each field usually has four related macros: `_offset` for the DWORD index in the packet, `_mask` for the unshifted field width, `_shift` for the target bit position, and an uppercase field helper that computes `((x) & mask) << shift`.

For `SDMA_AQL_PKT_COPY_LINEAR`, the chunk exposes:

- Header fields: `RELEASE_FENCE_SCOPE`, `RESERVED`, `OP`, and `SUBOP`. These complete the common AQL header encoding started before this range. In this packet, `op` is a 4-bit field at bit 16 and `subop` is a 3-bit field at bit 20.
- `RESERVED_DW1` at DWORD 1, plus reserved payload slots at DWORDs 10 through 13. These preserve the fixed 16-DW packet footprint.
- `RETURN_ADDR_LO` and `RETURN_ADDR_HI` at DWORDs 2 and 3, carrying a 64-bit return address split into low and high halves.
- `COUNT` at DWORD 4, with a `0x003FFFFF` mask. This limits the encoded linear-copy byte/count field to 22 bits in this ABI.
- `PARAMETER_DST_SW` and `PARAMETER_SRC_SW` at DWORD 5, both 2-bit fields, shifted to bits 16 and 24 respectively.
- `SRC_ADDR_LO`/`SRC_ADDR_HI` at DWORDs 6 and 7 and `DST_ADDR_LO`/`DST_ADDR_HI` at DWORDs 8 and 9, each exposing the full 32-bit low/high halves of a 64-bit address.
- `COMPLETION_SIGNAL_LO` and `COMPLETION_SIGNAL_HI` at DWORDs 14 and 15, carrying the 64-bit signal address written when the AQL operation completes.

For `SDMA_AQL_PKT_BARRIER_OR`, the chunk exposes:

- Header fields at DWORD 0: `FORMAT` in bits 0-7, `BARRIER` at bit 8, `ACQUIRE_FENCE_SCOPE` in bits 9-10, `RELEASE_FENCE_SCOPE` in bits 11-12, `RESERVED` in bits 13-15, `OP` in bits 16-19, and `SUBOP` in bits 20-22.
- `RESERVED_DW1` at DWORD 1.
- Five dependent signal addresses: `DEPENDENT_ADDR_0` through `DEPENDENT_ADDR_4`, each split into `_LO` and `_HI` macros and occupying DWORD pairs 2/3, 4/5, 6/7, 8/9, and 10/11.
- `RESERVED_DW12` and `RESERVED_DW13` at DWORDs 12 and 13.
- `COMPLETION_SIGNAL_LO` and `COMPLETION_SIGNAL_HI` at DWORDs 14 and 15.

The packet constants defined earlier in the file, especially `HEADER_AGENT_DISPATCH`, `HEADER_BARRIER`, `SDMA_OP_AQL_COPY`, and `SDMA_OP_AQL_BARRIER_OR`, are the natural symbolic values used with these field macros even though they are outside this exact range.

## Control Flow

This chunk has no executable control flow. Its "flow" is the packet word order imposed by the offsets:

1. A caller builds DWORD 0 from the relevant AQL header fields.
2. The caller writes each payload field into the packet slot identified by its `_offset`.
3. Address values are split by the caller into low and high 32-bit halves and packed into consecutive DWORDs.
4. The completed packet is submitted through whatever SDMA AQL queue/ring path consumes Navi10 SDMA packet layouts.

The SDMA firmware/hardware then interprets the resulting memory according to this ABI. The macros themselves do not validate whether fields such as format, op, subop, fence scope, swizzle mode, count, or addresses are semantically valid for the selected packet.

## State and Persistence

The header has no mutable C state and persists nothing by itself. The persistent state affected by these definitions is external:

- Source code compiled against this header bakes the bit positions, masks, and packet offsets into packet construction.
- AQL packets constructed from these macros live in queue/ring memory until consumed by SDMA hardware.
- Return addresses, dependent addresses, and completion signal addresses point at memory objects managed elsewhere, typically queue, signal, or driver-managed GPU-visible memory.
- Reserved DWORDs and reserved header bits are part of the hardware ABI. Their values may affect forward compatibility or hardware behavior if callers fail to zero them.

Because these are preprocessor macros, every consumer gets the same constants at compile time; there is no runtime discovery or version negotiation in this file.

## Dependencies and Integration Points

The direct dependency is the Navi10 SDMA packet ABI. The file is part of AMDGPU's SDMA packet-definition family and mirrors similar generated packet headers for other ASIC generations such as Vega and later SDMA IPs.

Likely integration points are:

- SDMA command submission paths that include this header to encode packet DWORDs for Navi10-era devices.
- KFD/HSA AQL queue handling, where `HEADER_AGENT_DISPATCH` and `HEADER_BARRIER` packet formats and AQL completion/dependency signal addresses are meaningful.
- Ring or queue buffer emitters that split GPU virtual addresses into 32-bit low/high words and use the `_offset` macros to fill fixed packet slots.
- Test/debug tooling that decodes SDMA packet buffers using the same offsets and masks.

The chunk does not include Linux kernel headers, AMDGPU structs, register access helpers, or DRM scheduler APIs directly. Its coupling is at the binary packet format boundary.

## Risks and Fragile Areas

- The macros silently truncate inputs to their masks. A too-large copy count, fence scope, op/subop, swizzle value, or reserved-field value will be masked rather than rejected.
- `_offset` values are fixed DWORD positions. A one-DWORD drift in an emitter would turn addresses, counts, or completion signals into the wrong payload fields and can cause SDMA faults or memory corruption.
- The address macros accept full 32-bit halves but do not enforce address alignment, address-space validity, GPU accessibility, or signal-object lifetime.
- `SDMA_AQL_PKT_COPY_LINEAR_COUNT` is only 22 bits wide. Callers must segment larger copies or use another path; the macro will not flag overflow.
- Reserved fields are exposed as packable macros. They should normally be zero unless a hardware specification requires otherwise; setting them opportunistically can break on Navi10 firmware/hardware.
- AQL barrier-or supports exactly five dependent addresses in this layout. Higher-level queue logic must not assume an arbitrary dependency count can fit in one packet.
- This Navi10 layout differs from newer SDMA packet headers, which may add fields such as cache policy or CPV bits. Cross-generation code must choose the correct packet header for the ASIC rather than reusing this layout generically.
- The chunk begins mid-definition of `SDMA_AQL_PKT_COPY_LINEAR`; maintaining or reviewing only this range requires checking the preceding header fields for the complete packet.

## Test and Validation Signals

Useful validation is mostly integration-level because the chunk itself has no functions to unit test:

- Compile coverage for all consumers that include `navi10_sdma_pkt_open.h`, catching macro name drift or missing definitions.
- Packet encoder tests that assert expected DWORD values for representative AQL copy-linear and barrier-or packets, including boundary values for `COUNT`, fence scopes, `op`, `subop`, and swizzle fields.
- Runtime SDMA copy tests on Navi10 hardware that verify small and maximum-in-field linear copies, correct source/destination addressing, and completion signal updates.
- AQL barrier tests that submit zero through five dependencies and verify the completion signal is not written until the expected dependent signals are satisfied.
- Negative or robustness tests for oversized counts and invalid dependency/signal addresses should verify that higher-level code rejects or segments work before these macros mask values.
- Debug traces or ring dumps should decode DWORDs 0 through 15 consistently with the `_offset` definitions in this chunk.
