# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1_0_pkt_open.h

Chunk: `subset-b-001359`
Covered source range: lines 1-4513 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1_0_pkt_open.h`

## Purpose

This chunk is the front and middle of the SDMA v7.1.0 packet definition header used by AMDGPU code to assemble SDMA command streams. It is a generated-style C preprocessor interface: it declares operation IDs, sub-operation IDs, cache/GCR control bit helpers, and packet-specific field macros that map semantic fields onto 32-bit command dwords. The macros are consumed by ring and queue submission code that writes raw dwords into SDMA command buffers for the GPU firmware/hardware parser.

There are no C functions, structs, enums, or storage objects in this range. The "API" is entirely macro based. Each packet section follows the same pattern:

- `<packet>_<word>_<field>_offset`: dword index in the packet.
- `<packet>_<word>_<field>_mask`: unshifted field mask.
- `<packet>_<word>_<field>_shift`: bit position in the dword.
- `<packet>_<word>_<FIELD>(x)`: helper that masks and shifts a caller-supplied value into packet position.

The file begins with the common SDMA opcode namespace:

- `SDMA_OP_*`: top-level packet opcodes for NOP, COPY, WRITE, INDIRECT, FENCE, TRAP, SEM, POLL_REGMEM, COND_EXE, ATOMIC, CONST_FILL, PTEPDE, TIMESTAMP, SRBM_WRITE, PRE_EXE, GPUVM_INV, GCR_REQ, and DUMMY_TRAP.
- `SDMA_SUBOP_*`: sub-opcodes for timestamp variants, copy variants, write variants, PTE/PDE variants, memory increment/data fill, poll/write/verify, and VM invalidation.
- `HEADER_AGENT_DISPATCH`, `HEADER_BARRIER`, `SDMA_OP_AQL_COPY`, and `SDMA_OP_AQL_BARRIER_OR` for AQL-style headers.
- `SDMA_GCR_*` helpers for global cache request control bits and range/sequence fields.
- `SDMA_DCC_*` helpers for DCC metadata/configuration fields such as data format, number type, read/write compression modes, and compression block sizes.

## Packet Families In This Chunk

Lines 1-4513 cover the following packet definition sections:

- Copy packets: `SDMA_PKT_COPY_LINEAR`, `SDMA_PKT_COPY_LINEAR_BC`, `SDMA_PKT_COPY_DIRTY_PAGE`, `SDMA_PKT_COPY_PHYSICAL_LINEAR`, `SDMA_PKT_COPY_BROADCAST_LINEAR`, `SDMA_PKT_COPY_LINEAR_SUBWIN`, `SDMA_PKT_COPY_LINEAR_SUBWIN_LARGE`, `SDMA_PKT_COPY_LINEAR_SUBWIN_BC`, `SDMA_PKT_COPY_TILED`, `SDMA_PKT_COPY_TILED_BC`, `SDMA_PKT_COPY_L2T_BROADCAST`, `SDMA_PKT_COPY_T2T`, `SDMA_PKT_COPY_T2T_BC`, `SDMA_PKT_COPY_TILED_SUBWIN`, `SDMA_PKT_COPY_TILED_SUBWIN_BC`, and `SDMA_PKT_COPY_STRUCT`.
- Write packets: `SDMA_PKT_WRITE_UNTILED`, `SDMA_PKT_WRITE_TILED`, `SDMA_PKT_WRITE_TILED_BC`, and `SDMA_PKT_WRITE_INCR`.
- VM/page-table packets: `SDMA_PKT_PTEPDE_COPY`, `SDMA_PKT_PTEPDE_COPY_BACKWARDS`, `SDMA_PKT_PTEPDE_RMW`, and `SDMA_PKT_VM_INVALIDATION`.
- Synchronization/control packets: `SDMA_PKT_INDIRECT`, `SDMA_PKT_SEMAPHORE`, `SDMA_PKT_MEM_INCR`, `SDMA_PKT_FENCE`, `SDMA_PKT_PRE_EXE`, `SDMA_PKT_COND_EXE`, and the beginning of `SDMA_PKT_POLL_REGMEM`.
- Register/system packets: `SDMA_PKT_REGISTER_RMW` and `SDMA_PKT_SRBM_WRITE`.
- Fill packets: `SDMA_PKT_CONSTANT_FILL` and `SDMA_PKT_DATA_FILL_MULTI`.

The assigned range ends inside the `SDMA_PKT_POLL_REGMEM` section. This chunk includes the poll/regmem header fields (`op`, `sub_op`, `cache_policy`, `cpv`, `hdp_flush`, `func`, `mem_poll`) through line 4513, but the address/value/mask/retry fields continue after this chunk and belong to a later chunk.

## Important Macro Contracts

The copy packet definitions dominate this chunk. They provide packet layouts for linear copies, physical linear copies, broadcast copies, linear subwindow copies, tiled-to-linear/linear-to-tiled transfers, tiled-to-tiled transfers, block-compressed variants, dirty-page copies, and structured buffer copies. Important fields include source/destination 64-bit addresses split into low/high dwords, byte or element counts, tiling geometry, rectangle dimensions, slice pitches, swizzle modes, cache policies, compression metadata, DCC controls, TMZ/encryption flags, CPV flags, broadcast flags, and detile/DCC direction bits.

The write packet definitions encode SDMA writes into untiled or tiled memory. They include destination addresses, geometry/tiling fields, cache policy or swizzle fields, count fields, and inline `DATA0` payload words. `SDMA_PKT_WRITE_INCR` adds mask/init/increment dwords for incrementing writes over a count.

The PTE/PDE packet definitions provide copy, backwards-copy, and read-modify-write layouts for GPU page table maintenance. These macros expose source/destination addresses, masks, values, PTE sizing/direction fields, PTE/PDE operation selectors, cache-policy fields, memory type fields, snoop/GPA/system bits, and counts. These are integration-sensitive because malformed values can corrupt GPU VM page tables or cause stale translations.

The synchronization and control packet definitions cover indirect buffers, semaphores, memory increment, fences, conditional execution, pre-execution, and poll/regmem header setup. These macros are used to point the SDMA engine at secondary command buffers, signal or wait on GPU-visible memory, write fence values, conditionally skip/execute command ranges, and poll registers or memory with specified comparison functions.

The register/system packet definitions encode register RMW and SRBM writes. They carry register addresses/aperture IDs, masks, values, byte enables, stride, and register counts. These packets can modify device control state, so callers must provide addresses and aperture IDs from trusted register definitions.

## Control Flow

This header has no runtime control flow. Its control-flow role is indirect: callers construct an SDMA command stream by writing dwords in the order implied by each packet section's offsets. The first dword is typically a header with `OP()` and sometimes `SUB_OP()` plus mode bits. Subsequent dwords carry addresses, counts, dimensions, masks, or payloads at fixed indexes. SDMA hardware/firmware then interprets the dword stream and performs memory, register, synchronization, VM, or cache operations.

A concrete local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c`, which includes this header and emits an SDMA queue packet by composing `SDMA_PKT_COPY_LINEAR_HEADER_OP(SDMA_OP_WRITE)`, `SDMA_PKT_COPY_LINEAR_HEADER_SUB_OP(SDMA_SUBOP_WRITE_LINEAR)`, `SDMA_PKT_WRITE_UNTILED_DW_3_COUNT(0)`, and `SDMA_PKT_NOP_HEADER_OP(SDMA_OP_NOP)` into a queue buffer. The packet header bit positions are shared enough that the code can use a packet-family header macro to emit the common opcode/sub-op header bits, while the later dwords use the specific write packet layout.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It does, however, describe packets that mutate persistent GPU-visible state when executed:

- Copy/write/fill packets modify VRAM, GTT, or other GPU-addressable memory.
- PTE/PDE and VM invalidation packets affect GPU virtual memory tables and translation visibility.
- Fence, semaphore, memory increment, and poll packets communicate completion/progress through memory or registers.
- Register RMW and SRBM writes modify hardware register state.
- GCR-related helpers and cache-policy fields influence cache flush/invalidate/writeback behavior for command effects.

Because the macros silently mask arguments, a caller can pass values that are out of architectural range and get truncated into a valid-looking packet. Correctness depends on higher-level SDMA emitters validating byte counts, alignment, address ranges, tiling metadata, VMIDs, cache policies, and packet length before submission.

## Dependencies And Integration Points

This header has no includes and depends only on C preprocessor arithmetic and integer constants. Its real dependency is the SDMA v7.1.0 packet ABI: field masks, shifts, and dword offsets must match the hardware packet parser exactly.

Primary integration points are AMDGPU ring/IB emitters that allocate a command buffer, call these macros while writing dwords, update write pointers, and ring doorbells. It also integrates with:

- AMDGPU VM update paths that need PTE/PDE copy/RMW and VM invalidation packets.
- Buffer copy, fill, and migration paths that use linear, tiled, physical, dirty-page, and broadcast copy packets.
- Fence and semaphore paths that synchronize CPU/GPU or inter-engine work.
- MES queue setup and validation paths, including the observed `mes_v12_1.c` SDMA queue emission.
- Register access helpers that emit SRBM write or register RMW packets.

The chunk is part of a family of architecture-specific packet headers under the same AMDGPU directory. Similar packet macro names exist for older SDMA generations, so include selection must match the hardware generation. Accidentally mixing v7.1.0 packet fields with a different SDMA engine version is a high-risk ABI bug.

## Risks

- Field truncation is silent. Every builder macro masks `x` before shifting, so invalid values become truncated packet fields instead of compile-time or runtime errors.
- Packet layout bugs are severe. A wrong offset, mask, or shift writes a syntactically valid dword stream with incorrect semantics, potentially causing memory corruption, hangs, bad fences, VM faults, or register misprogramming.
- Macro names are packet-specific but some header fields are layout-compatible across packets. This encourages reuse like `SDMA_PKT_COPY_LINEAR_HEADER_OP(SDMA_OP_WRITE)`, which works only if the common header bit placement remains compatible.
- Address fields are split manually into low/high dwords by callers. Incorrect splitting, alignment, or address-space selection can target the wrong GPU memory or register aperture.
- Tiled/DCC/block-compressed packet families have many geometry and metadata fields. Mismatched width/height/depth, pitch, swizzle, DCC metadata, or compression settings can corrupt image data in ways that may only appear under specific formats.
- PTE/PDE RMW/copy packets and VM invalidation packets are especially sensitive because they affect translation state. Ordering, cache policy, and invalidation omissions can create stale mappings or GPU page faults.
- This chunk ends mid-`SDMA_PKT_POLL_REGMEM`; any research or generated validation for the full header must merge the later chunk before treating poll/regmem as fully covered.

## Test Signals

Useful signals for this header are mostly integration and hardware-facing rather than unit-testable logic:

- Compile coverage for every C file that includes `sdma_v7_1_0_pkt_open.h`; missing or renamed macros should fail builds immediately.
- Ring self-tests that emit NOP, WRITE, FENCE, INDIRECT, POLL_REGMEM, and TRAP packets and verify completion/fence memory.
- SDMA copy/fill tests covering linear copies, large copies, TMZ/encrypted copies, physical copies, dirty-page copies, broadcast copies, and count boundary values.
- Tiled/DCC/block-compressed copy tests comparing GPU output against CPU reference images across swizzle modes, dimensions, mip levels, pitches, metadata settings, and detile directions.
- VM update tests that exercise PTE/PDE copy/RMW/backwards-copy and validate subsequent GPU access plus required invalidation behavior.
- Register write/RMW tests limited to safe scratch or test registers, validating aperture ID, mask, stride, byte enable, and multi-register behavior.
- Poll/fence/semaphore timeout tests that ensure retry/interval fields and comparison function fields lead to expected completion or timeout behavior once the later poll/regmem fields are included.
