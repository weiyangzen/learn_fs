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
