# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vega10_sdma_pkt_open.h

## Purpose

`vega10_sdma_pkt_open.h` is a generated-style packet layout header for Vega10-family SDMA command streams. It contains no executable code, storage, or exported C objects. Its job is to give packet emitters symbolic opcodes, sub-opcodes, dword offsets, masks, shifts, and packing macros for constructing binary SDMA packets written into GPU command buffers.

The file covers ordinary SDMA packets and AQL SDMA packets. The ordinary packet families include linear, tiled, broadcast, sub-window, structure, PTE/PDE, write, fill, poll, atomic, semaphore, fence, indirect, timestamp, trap, dummy trap, pre-execute, conditional execute, SRBM write, and NOP packets. The AQL packet families cover a generic AQL header, AQL linear copy, and AQL barrier-or packet.

## Important APIs, Types, And Macros

The public surface is entirely macro-based:

- Top-level opcode macros define packet classes: `SDMA_OP_NOP`, `SDMA_OP_COPY`, `SDMA_OP_WRITE`, `SDMA_OP_INDIRECT`, `SDMA_OP_FENCE`, `SDMA_OP_TRAP`, `SDMA_OP_SEM`, `SDMA_OP_POLL_REGMEM`, `SDMA_OP_COND_EXE`, `SDMA_OP_ATOMIC`, `SDMA_OP_CONST_FILL`, `SDMA_OP_PTEPDE`, `SDMA_OP_TIMESTAMP`, `SDMA_OP_SRBM_WRITE`, `SDMA_OP_PRE_EXE`, and `SDMA_OP_DUMMY_TRAP`.
- Sub-opcode macros specialize shared packet classes, for example `SDMA_SUBOP_COPY_LINEAR`, `SDMA_SUBOP_COPY_TILED`, `SDMA_SUBOP_COPY_T2T_SUB_WIND`, `SDMA_SUBOP_PTEPDE_COPY`, `SDMA_SUBOP_PTEPDE_RMW`, and timestamp/poll/fill sub-ops.
- `SDMA_PKT_HEADER_OP(x)` and `SDMA_PKT_HEADER_SUB_OP(x)` provide generic header field packing for the common op/sub-op fields.
- Every packet field has a regular macro quartet: `<packet>_<word>_<field>_offset`, `_mask`, `_shift`, and a packing helper such as `SDMA_PKT_COPY_LINEAR_COUNT_COUNT(x)`.
- The AQL portion uses the same field pattern with names such as `SDMA_AQL_PKT_HEADER_HEADER_FORMAT(x)`, `SDMA_AQL_PKT_COPY_LINEAR_COMPLETION_SIGNAL_LO_COMPLETION_SIGNAL_31_0(x)`, and `SDMA_AQL_PKT_BARRIER_OR_DEPENDENT_ADDR_0_LO_DEPENDENT_ADDR_0_31_0(x)`.

Important packet groups and their roles:

- Copy packets: `SDMA_PKT_COPY_LINEAR`, `SDMA_PKT_COPY_DIRTY_PAGE`, `SDMA_PKT_COPY_PHYSICAL_LINEAR`, `SDMA_PKT_COPY_BROADCAST_LINEAR`, `SDMA_PKT_COPY_LINEAR_SUBWIN`, `SDMA_PKT_COPY_TILED`, `SDMA_PKT_COPY_L2T_BROADCAST`, `SDMA_PKT_COPY_T2T`, `SDMA_PKT_COPY_TILED_SUBWIN`, and `SDMA_PKT_COPY_STRUCT`.
- Write/fill packets: `SDMA_PKT_WRITE_UNTILED`, `SDMA_PKT_WRITE_TILED`, `SDMA_PKT_WRITE_INCR`, `SDMA_PKT_CONSTANT_FILL`, and `SDMA_PKT_DATA_FILL_MULTI`.
- Page-table packets: `SDMA_PKT_PTEPDE_COPY`, `SDMA_PKT_PTEPDE_COPY_BACKWARDS`, and `SDMA_PKT_PTEPDE_RMW`.
- Synchronization/control packets: `SDMA_PKT_INDIRECT`, `SDMA_PKT_SEMAPHORE`, `SDMA_PKT_FENCE`, `SDMA_PKT_TRAP`, `SDMA_PKT_DUMMY_TRAP`, `SDMA_PKT_NOP`, `SDMA_PKT_PRE_EXE`, and `SDMA_PKT_COND_EXE`.
- Poll/verify packets: `SDMA_PKT_POLL_REGMEM`, `SDMA_PKT_POLL_REG_WRITE_MEM`, `SDMA_PKT_POLL_DBIT_WRITE_MEM`, and `SDMA_PKT_POLL_MEM_VERIFY`.
- Timestamp and atomic packets: `SDMA_PKT_ATOMIC`, `SDMA_PKT_TIMESTAMP_SET`, `SDMA_PKT_TIMESTAMP_GET`, and `SDMA_PKT_TIMESTAMP_GET_GLOBAL`.

## Control Flow

There is no runtime control flow in this header. Runtime behavior emerges when SDMA ring emitters combine the macros into ordered 32-bit dwords. A typical flow is:

1. Emit a packet header dword with `*_HEADER_OP(SDMA_OP_*)` and, when applicable, `*_HEADER_SUB_OP(SDMA_SUBOP_*)`.
2. Emit payload dwords in the numeric order defined by each field's `_offset`.
3. Split 64-bit GPU or system addresses into low and high dwords with the corresponding `*_ADDR_LO_*` and `*_ADDR_HI_*` field helpers.
4. Set mode bits such as `tmz`, `encrypt`, `broadcast`, `detile`, `mip_max`, `vmid`, cache/snoop flags, or AQL fence scopes as required by the packet type.

The command processor firmware and SDMA hardware interpret the resulting dword stream; this file does not validate packet sequencing or constraints.

## State And Persistence Behavior

The header is stateless. It neither reads nor writes kernel memory, hardware registers, GPU memory, files, nor persistent configuration. The state it influences is external: SDMA command buffers, GPU-visible memory, interrupt side effects, fences, and page table updates produced by callers that use these macros.

Because the helpers do not cast or size-check inputs, state correctness depends on callers passing already-normalized field values. Values outside a field width are silently masked.

## Dependencies

The file only depends on the C preprocessor and its include guard. It does not include other headers. Semantic dependencies are external and hardware-specific:

- SDMA firmware/hardware packet ABI for Vega10-compatible engines.
- AMDGPU packet emitter code that writes ring dwords.
- Address and tiling metadata from memory-management and graphics code.
- AQL consumers that need SDMA AQL packet layout compatibility.

## Integration Points

This header integrates with AMDGPU code that builds SDMA command streams. A repository search shows the broader tree has multiple ASIC-specific `*_sdma_pkt_open.h` headers with similar macro naming. Packet emitters include the appropriate ASIC header through their SDMA implementation or shared packet-building code.

Important integration expectations:

- Offsets are dword indexes, not byte offsets.
- Address fields often carry alignment-implied bit ranges, for example timestamp write address macros use `write_addr_31_3` shifted by 3.
- Count masks differ by packet type, such as 22-bit linear copy counts, 20-bit tiled counts, 19-bit PTE/PDE counts, and full 32-bit structure fields.
- The `tmz` and `encrypt` bits are security-sensitive because they influence trusted-memory/encrypted copy behavior.
- Broadcast and tiled packet layouts have additional destination, swizzle, pitch, slice-pitch, dimension, and mip fields that must match surface metadata.

## Risks

- Silent truncation is the main risk. Every packing macro masks `x` and shifts it; an invalid large value may produce a syntactically valid but semantically wrong packet.
- Packet definitions are hardware ABI. A wrong offset, mask, or shift can corrupt GPU memory, page tables, fences, or synchronization state.
- Header op/sub-op combinations are not type-safe. Callers can combine macros from one packet family with opcodes from another.
- 64-bit address splitting must be correct and alignment rules must be satisfied by callers.
- Page table packets and atomics can mutate memory-management state. Incorrect masks or counts can be high impact.
- AQL packet fields include completion signals and dependency addresses; bad values can break queue synchronization.

## Test Signals

Useful validation signals are mostly integration-level:

- Build coverage for all SDMA emitters that include this header.
- GPU ring tests that emit linear copy, tiled copy, fill, fence, semaphore, timestamp, poll, and indirect packets.
- IGT or AMDGPU selftests that verify SDMA copy correctness across VRAM, GTT, TMZ/encrypted memory, and tiled surfaces.
- VM/page-table stress tests that exercise PTE/PDE copy/RMW/backwards packets.
- Fault injection or debug logs around SDMA timeouts, bad fences, page faults, or ring hangs after packet changes.
- Static checks comparing these generated masks/offsets against the authoritative hardware register packet XML or generated source.
