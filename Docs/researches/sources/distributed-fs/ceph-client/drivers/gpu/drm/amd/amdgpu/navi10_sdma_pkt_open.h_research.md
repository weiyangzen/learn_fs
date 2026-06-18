# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/navi10_sdma_pkt_open.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001350`: lines 1-4599, `Docs/researches/chunks/subset-b-001350_research.md`
- `subset-b-001351`: lines 4600-4886, `Docs/researches/chunks/subset-b-001351_research.md`

## Chunk Research

### subset-b-001350: lines 1-4599

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/navi10_sdma_pkt_open.h lines 1-4599

## Scope

This chunk covers the Navi10 SDMA packet-definition header from the license/include guard through line 4599. It includes generic SDMA opcode constants, GCR control helpers, all standard SDMA packet field macros through `SDMA_AQL_PKT_HEADER`, and the opening header fields of `SDMA_AQL_PKT_COPY_LINEAR`. The source file continues past this chunk with the rest of AQL copy-linear and barrier-or packet fields, so this document intentionally does not synthesize the final per-file report.

## Purpose

`navi10_sdma_pkt_open.h` is an ASIC-specific packet schema for AMDGPU SDMA 5.x hardware. It gives ring and indirect-buffer emitters symbolic constants for building 32-bit command words consumed by Navi10-class SDMA engines. The header does not execute code or allocate state; it encodes the hardware contract: opcode values, sub-opcode values, dword offsets, bit masks, shifts, and `FIELD(x)` helpers that pack caller-supplied values into command-stream dwords.

The file is consumed by `sdma_v5_0.c` and `sdma_v5_2.c`, which include this header and use the macros while writing commands to `amdgpu_ring` buffers and SDMA indirect buffers. Similar generated packet headers exist for older and newer ASIC families, so this file is the Navi10-family member of a larger per-IP packet-description pattern.

## Packet Model and Macro Pattern

Every packet section follows a generated naming scheme:

- `SDMA_PKT_<PACKET>_<WORD>_<field>_offset` gives the dword index inside the packet.
- `SDMA_PKT_<PACKET>_<WORD>_<field>_mask` gives the unshifted field mask.
- `SDMA_PKT_<PACKET>_<WORD>_<field>_shift` gives the bit position inside that dword.
- `SDMA_PKT_<PACKET>_<WORD>_<FIELD>(x)` masks `x` and shifts it into place for OR-ing with other fields.

The top-level `SDMA_PKT_HEADER_OP(x)` and `SDMA_PKT_HEADER_SUB_OP(x)` helpers encode the common low 16 header bits used by most SDMA packets. Packet-specific header helpers duplicate the same pattern when a caller wants a section-scoped macro name. Most address fields are split into `_LO` and `_HI` dwords with full-width `0xFFFFFFFF` masks; count, pitch, coordinate, cache-policy, VMID, and control fields use narrower masks documented by their names.

## Important Constants and Packet Families

Top-level opcodes define the SDMA command classes: `NOP`, `COPY`, `WRITE`, `INDIRECT`, `FENCE`, `TRAP`, `SEM`, `POLL_REGMEM`, `COND_EXE`, `ATOMIC`, `CONST_FILL`, `PTEPDE`, `TIMESTAMP`, `SRBM_WRITE`, `PRE_EXE`, `GPUVM_INV`, `GCR_REQ`, and `DUMMY_TRAP`. Sub-opcodes refine timestamp, copy, write, PTE/PDE, multi-fill, poll/write-memory, poll-dbit, poll-verify, and VM invalidation forms. AQL constants define packet header formats for agent dispatch, barrier, AQL copy, and barrier-or.

The chunk defines packet layouts for these major groups:

- Copy packets: linear, broadcast linear, dirty-page, physical linear, linear sub-window, tiled, tiled sub-window, linear-to-tiled broadcast, tiled-to-tiled, and BC variants.
- Write and fill packets: untiled write, tiled write, BC tiled write, incrementing write, constant fill, and multi-data fill.
- GPUVM/PTE packets: PTE/PDE copy, backwards copy, read-modify-write, VM invalidation, GPUVM invalidation, and GCR request.
- Ring control and synchronization packets: indirect buffer execution, semaphore, fence, conditional execution, pre-execution, poll-regmem, poll-reg-write-mem, poll-dbit-write-mem, poll-memory-verify, NOP, trap, dummy trap, timestamp set/get/global-get, atomic, and SRBM write.
- AQL packets within this chunk: generic AQL header and the start of AQL copy-linear header fields through `release_fence_scope_mask` at line 4599.

## Control Flow and Integration

There is no C control flow in this header. The effective control flow appears in callers that append dwords to a ring or IB:

1. Emit a header using `SDMA_PKT_HEADER_OP()` or a packet-specific `_HEADER_OP()` plus the required `SDMA_OP_*` and `SDMA_SUBOP_*`.
2. Emit subsequent dwords in the exact order implied by each field's `_offset`.
3. Split 64-bit GPU addresses with `lower_32_bits()` and `upper_32_bits()`.
4. Commit the ring or schedule the IB so SDMA firmware/hardware fetches and executes the packet stream.

`sdma_v5_0_ring_test_ring()` and `sdma_v5_0_ring_test_ib()` use the write-linear packet fields to write `0xDEADBEEF` into a writeback slot. VM helpers use copy/write/PTE packet fields to update page tables. Flush and synchronization paths use `POLL_REGMEM`, `FENCE`, `TRAP`, and `GCR_REQ` fields. `sdma_v5_0_ring_insert_nop()` uses `SDMA_PKT_NOP_HEADER_COUNT()` for burst NOP packing.

The GCR helper constants at the top of the file (`SDMA_GCR_*`) build the `gcr_cntl` value that caller code splits into `SDMA_PKT_GCR_REQ_PAYLOAD2_GCR_CONTROL_15_0()` and `SDMA_PKT_GCR_REQ_PAYLOAD3_GCR_CONTROL_18_16()`. This connects SDMA command emission to cache invalidation/writeback behavior for GL1/GL2/GLK/GLM/GLV and range handling.

## State and Persistence

The header itself has no runtime state, persistence, memory ownership, locking, or side effects. Its persistence is compile-time: macro values become constants embedded into emitted SDMA command streams. Hardware-visible state changes occur only after callers submit packets built with these macros. Those side effects include memory copies, memory writes, page-table updates, fences, semaphores, timestamp writes, atomics, cache/TLB invalidation, SRBM register writes, and traps.

Because the macros mask inputs before shifting, out-of-range high bits are silently truncated rather than reported. Callers must still validate packet length, address alignment, count units, byte-vs-dword semantics, cache policy, TMZ/encryption flags, VMID, and packet-specific reserved fields before emission.

## Dependencies

This header depends only on C preprocessor semantics and fixed-width integer assumptions in the including C files. It is tied tightly to the Navi10 SDMA packet ABI and is included by SDMA 5.x driver implementations. Runtime integration depends on AMDGPU core objects and helpers outside this file: `amdgpu_ring_write()`, `amdgpu_ring_alloc()`, `amdgpu_ring_commit()`, `amdgpu_ib`, fence scheduling, writeback memory, VM update paths, SOC15 register helpers, and firmware/hardware SDMA command processors.

The packet layouts are also implicitly coupled to hardware documentation and to any userspace/kernel expectations about SDMA packet binary format. Changes must stay synchronized with the SDMA engine generation selected by the including driver, not with unrelated ASIC packet headers that share similar macro names but may have different field widths or offsets.

## Risks and Fragile Areas

- Silent truncation is deliberate but risky: every `FIELD(x)` helper masks before shifting, so invalid large counts, coordinates, VMIDs, or cache-control values can become valid-looking but wrong packet fields.
- Packet dword ordering is not enforced by types. A caller that uses a correct macro at the wrong dword index will compile and may hang or corrupt GPU memory.
- Many macros share generic names such as `COUNT`, `ADDR_LO`, `DATA`, `SW`, and `TMZ` under packet-specific prefixes. Copying code between packet families can accidentally preserve the wrong offset or unit semantics.
- Address fields expose raw 64-bit GPU/physical address pieces. Misalignment or wrong address space selection can affect VRAM, GTT, page tables, or privileged register targets.
- Cache and VM invalidation fields (`GPUVM_INV`, `VM_INVALIDATION`, `GCR_REQ`) are synchronization-sensitive. Missing bits or wrong VMID/range fields can leave stale translations or cache lines visible to later work.
- Privileged packets such as `SRBM_WRITE`, PTE/PDE operations, atomics, and indirect buffer execution assume trusted kernel emission. They are high-impact if reached with corrupted parameters.
- The assigned chunk stops in the middle of `SDMA_AQL_PKT_COPY_LINEAR`; line 4599 includes only part of its header-field definitions. Consumers of this research must merge with the following chunk before making whole-file statements about AQL packet support.

## Test and Validation Signals

Useful validation comes from SDMA ring and IB tests rather than from this header alone. Positive signals include successful `sdma_v5_0_ring_test_ring()` and `sdma_v5_0_ring_test_ib()` writeback checks, successful VM page-table copy/write updates, fences completing after `SDMA_OP_FENCE`, traps interrupting as expected, NOP padding not changing ring progress, and GCR/GPUVM invalidation paths avoiding stale-translation faults.

Regression signals include SDMA ring timeouts, failed IB scheduling, writeback slots retaining old values after write packets, VM faults after PTE/PDE updates, cache/TLB coherency failures after GCR or GPUVM invalidations, bad-opcode or privileged-instruction interrupts, and hangs after poll/conditional/indirect packets. Static review should check generated macro values against the Navi10 SDMA packet specification and compare any edits against neighboring ASIC packet headers only as a sanity check, not as the source of truth.

### subset-b-001351: lines 4600-4886

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
