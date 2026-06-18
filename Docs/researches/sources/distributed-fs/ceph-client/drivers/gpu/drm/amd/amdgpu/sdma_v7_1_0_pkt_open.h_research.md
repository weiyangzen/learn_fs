# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1_0_pkt_open.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001359`: lines 1-4513, `Docs/researches/chunks/subset-b-001359_research.md`
- `subset-b-001360`: lines 4514-5673, `Docs/researches/chunks/subset-b-001360_research.md`

## Chunk Research

### subset-b-001359: lines 1-4513

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

### subset-b-001360: lines 4514-5673

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1_0_pkt_open.h lines 4514-5673

## Purpose

This chunk is the tail of the generated SDMA v7.1.0 packet-open header for the AMDGPU driver. It does not implement executable control flow; instead it exposes C preprocessor constants and field-pack helper macros for writing hardware command packets into SDMA ring buffers or AQL queues. The covered range starts in the middle of `SDMA_PKT_POLL_REGMEM` and continues through polling/writeback, atomics, timestamp, trap, GPUVM invalidation, GCR/cache request, NOP, and AQL copy/barrier packet layouts before closing the include guard.

Every packet definition follows the same contract:

- `<packet>_<word>_<field>_offset` gives the dword index inside the packet.
- `<packet>_<word>_<field>_mask` gives the unshifted accepted field width.
- `<packet>_<word>_<field>_shift` gives the bit shift inside that dword.
- `<packet>_<word>_<FIELD>(x)` masks `x` and shifts it into position.

The source intentionally keeps these definitions as raw macros so ring emission code can OR multiple fields into one dword without relying on packed C structs or compiler-specific bitfield layout.

## Important APIs, Types, And Packet Layouts

The chunk has no functions or types. The API surface is macro-only and consumed by SDMA packet builders elsewhere in the AMDGPU stack.

### `SDMA_PKT_POLL_REGMEM` Tail

The chunk begins after the `SDMA_PKT_POLL_REGMEM` header macros. It defines the payload dwords:

- `ADDR_LO` and `ADDR_HI` at offsets 1 and 2 hold the full 64-bit poll target address.
- `VALUE` at offset 3 is the compare value.
- `MASK` at offset 4 masks the loaded register/memory value before comparison.
- `DW5_INTERVAL(x)` encodes a 16-bit polling interval at bits 0-15 of dword 5.
- `DW5_RETRY_COUNT(x)` encodes a 12-bit retry count at bits 16-27 of dword 5.

The related header fields just before this chunk include `op`, `sub_op`, `cache_policy`, `cpv`, `hdp_flush`, comparison `func`, and `mem_poll`, so these payload fields are the state that the SDMA engine polls until the function condition is satisfied or retries expire.

### `SDMA_PKT_POLL_REG_WRITE_MEM`

This packet describes a register poll/read path that writes a result to memory:

- Header dword offset 0 exposes `op`, `sub_op`, `cache_policy`, and `cpv`.
- `SRC_ADDR_ADDR_31_2(x)` encodes a 30-bit register/source address shifted by 2 at dword 1, implying dword alignment.
- `DST_ADDR_LO` and `DST_ADDR_HI` at dwords 2 and 3 form the 64-bit memory destination.

The source address is narrower and aligned, while the destination is a full memory address. Callers must split the destination correctly and avoid passing unaligned source bits because the helper masks before shifting.

### `SDMA_PKT_POLL_DBIT_WRITE_MEM`

This packet writes memory based on dirty-bit or page tracking state:

- Header fields are `op`, `sub_op`, `ea`, `cache_policy`, and `cpv`.
- `DST_ADDR_LO`/`DST_ADDR_HI` at offsets 1 and 2 hold the memory destination.
- `START_PAGE_ADDR_31_4(x)` at offset 3 encodes a page address aligned to bit 4.
- `PAGE_NUM_PAGE_NUM_31_0(x)` at offset 4 provides a 32-bit page count.

The `ea` field is only 2 bits, and `START_PAGE` drops low four bits. Packet builders need to pass hardware-normalized page addresses/counts rather than byte-granular virtual addresses.

### `SDMA_PKT_POLL_MEM_VERIFY`

This packet compares memory ranges against a pattern and records results:

- Header fields: `op`, `sub_op`, `cache_policy`, `cpv`, and `mode`.
- `PATTERN` dword 1 contains the 32-bit compare pattern.
- Compare window 0 uses `CMP0_ADDR_START_LO/HI` and `CMP0_ADDR_END_LO/HI` at dwords 2-5.
- Compare window 1 uses `CMP1_ADDR_START_LO/HI` and `CMP1_ADDR_END_LO/HI` at dwords 6-9.
- `REC_ADDR_LO/HI` at dwords 10-11 provides the record/writeback address.
- Dword 12 is explicitly reserved.

The layout supports two independent 64-bit address ranges plus a 64-bit result location. The mode bit controls the verification semantic, while cache policy and CPV select memory handling.

### `SDMA_PKT_ATOMIC`

This packet encodes an SDMA atomic operation against a memory address:

- Header fields: `op`, `loop`, `tmz`, `cache_policy`, `cpv`, and a 7-bit `atomic_op` in bits 25-31.
- `ADDR_LO/HI` at dwords 1-2 identify the target address.
- `SRC_DATA_LO/HI` at dwords 3-4 provide the 64-bit source operand.
- `CMP_DATA_LO/HI` at dwords 5-6 provide the 64-bit compare operand for compare-and-swap style atomics.
- `LOOP_INTERVAL(x)` at dword 7 is a 13-bit retry/loop interval.

Security and memory-system behavior are part of the header: `tmz` selects trusted memory-zone behavior, `cache_policy` selects caching, and `cpv` participates in cache policy validity. The low-level macros do not enforce which `atomic_op` values require compare data.

### Timestamp Packets

`SDMA_PKT_TIMESTAMP_SET` writes an initial 64-bit timestamp value into the SDMA timestamp state:

- Header: `op` and `sub_op`.
- `INIT_DATA_LO/HI` at dwords 1-2 hold the 64-bit initial value.

`SDMA_PKT_TIMESTAMP_GET` writes a timestamp to a memory address:

- Header: `op`, `sub_op`, `l2_policy`, `llc_policy`, and `cpv`.
- `WRITE_ADDR_LO_WRITE_ADDR_31_3(x)` encodes bits 31:3 of the destination at dword 1, enforcing 8-byte alignment.
- `WRITE_ADDR_HI_WRITE_ADDR_63_32(x)` holds high address bits at dword 2.

`SDMA_PKT_TIMESTAMP_GET_GLOBAL` has the same destination and cache policy layout as `TIMESTAMP_GET` but uses the global timestamp sub-op. These packets are important for profiling, fence diagnostics, and synchronization timing because they persist timing data into GPU-accessible memory.

### Trap Packets

`SDMA_PKT_TRAP` and `SDMA_PKT_DUMMY_TRAP` both contain:

- Header dword with `op` and `sub_op`.
- `INT_CONTEXT_INT_CONTEXT(x)` at dword 1, a 28-bit interrupt context payload.

The regular trap is an interrupt/signaling packet. The dummy trap uses the same context layout but different opcode/sub-op semantics. The macro layer does not distinguish interrupt routing policy; it only packs the context field.

### `SDMA_PKT_GPUVM_INV`

This packet describes GPU virtual-memory invalidation and associated TLB/cache flush behavior:

- Header dword exposes `op` and `sub_op`.
- Payload dword 1 includes `per_vmid_inv_req` bits 0-15, 3-bit `flush_type` at bits 16-18, and per-level invalidation flags for `l2_ptes`, `l2_pde0`, `l2_pde1`, `l2_pde2`, and `l1_ptes` at bits 19-23.
- Payload dword 1 also includes `clr_protection_fault_status_addr`, `log_request`, and `four_kilobytes` at bits 24-26.
- Payload dword 2 has `S(x)` at bit 0 and `PAGE_VA_42_12(x)` in bits 1-31.
- Payload dword 3 has `PAGE_VA_47_43(x)` in bits 0-5.

This is a compact invalidation descriptor. It can request per-VMID invalidation, select flush type, target page ranges, and clear/log fault state. The split page VA fields mean callers must convert byte addresses into the exact page-address representation expected by hardware.

### `SDMA_PKT_GCR_REQ`

This packet emits a generic cache request over an address range:

- Header fields: `op` and `sub_op`.
- `PAYLOAD1_BASE_VA_31_7(x)` encodes low base virtual address bits starting at bit 7.
- `PAYLOAD2_BASE_VA_56_32(x)` encodes base bits 56:32.
- `PAYLOAD3_GCR_CONTROL_18_0(x)` carries the 19-bit cache control word.
- `PAYLOAD3_LIMIT_VA_15_7(x)`, `PAYLOAD4_LIMIT_VA_47_16(x)`, and `PAYLOAD5_LIMIT_VA_56_48(x)` encode the limit address.
- `PAYLOAD5_VMID(x)` encodes a 4-bit VMID in bits 26-29.

The top-of-file `SDMA_GCR_*` helpers complement this packet by building the `gcr_control_18_0` value, including range-is-PA, GL2/GL1 invalidation/writeback, GLK/GLM/GLV bits, and sequence/range controls. This packet is an integration point for cache coherence after page-table changes, migration, or explicit cache maintenance.

### `SDMA_PKT_NOP`

The NOP packet provides:

- Header `op`, `sub_op`, and 14-bit `count` at bits 16-29.
- `DATA0_DATA0(x)` at dword 1.

The `count` field lets emitters create variable-length NOP padding or embedded debug data. The macro only provides the first data dword layout; packet length policy is handled by the ring emitter.

### AQL Packet Header And AQL Copy

The AQL packet format uses a different header convention from the native SDMA packet macros:

- `format` at bits 0-7.
- `barrier` at bit 8.
- `acquire_fence_scope` at bits 9-10.
- `release_fence_scope` at bits 11-12.
- `reserved` at bits 13-15.
- 4-bit `op` at bits 16-19.
- 3-bit `subop` at bits 20-22.
- `cpv` at bit 28.

`SDMA_AQL_PKT_COPY_LINEAR` expands this header into a 16-dword linear copy descriptor:

- Dword 1 reserved.
- Dwords 2-3: 64-bit return address.
- Dword 4: 22-bit byte/count field.
- Dword 5: destination/source swizzle and cache policy fields (`dst_sw`, `dst_cache_policy`, `src_sw`, `src_cache_policy`).
- Dwords 6-7: 64-bit source address.
- Dwords 8-9: 64-bit destination address.
- Dwords 10-13 reserved.
- Dwords 14-15: 64-bit completion signal address/value pointer.

AQL integration suggests consumption by HSA-style queues or firmware/user-mode dispatch paths that use AQL packet conventions rather than the native SDMA ring packet header.

### `SDMA_AQL_PKT_BARRIER_OR`

The AQL barrier-or packet shares the AQL header layout and defines a 16-dword barrier descriptor:

- Dword 1 reserved.
- Dwords 2-11: five 64-bit dependent signal addresses, each split into low/high dwords.
- Dword 12: five 3-bit cache-policy fields, one per dependent address, placed at bits 0, 5, 10, 15, and 20.
- Dword 13 reserved.
- Dwords 14-15: 64-bit completion signal.

This models an AQL barrier that waits on or combines up to five dependencies and signals completion after the barrier condition is satisfied.

## Control Flow

There is no CPU-side control flow in this range. The logical flow is deferred to the SDMA micro-engine after a caller writes the packed dwords to a command buffer:

1. Caller chooses the packet opcode/sub-op constants from the earlier header section.
2. Caller builds dword 0 by OR-ing header field macros.
3. Caller writes remaining packet dwords using the payload macros and split-address helpers.
4. SDMA hardware interprets the packet in ring order or AQL queue order.
5. Poll, atomic, invalidation, timestamp, trap, and AQL barrier packets may cause hardware-visible memory writes, invalidations, interrupts, or completion-signal updates.

The header macros impose only bit placement. Ordering, packet length, ring reservation, write-pointer updates, and fence sequencing belong to the surrounding AMDGPU SDMA ring and queue code.

## State And Persistence Behavior

The header itself has no runtime storage. It affects persistent or externally visible state when used to build commands:

- Poll/write packets can persist register or dirty-bit derived values into GPU memory.
- `POLL_MEM_VERIFY` can write verification records to the `REC_ADDR` destination.
- `ATOMIC` mutates memory atomically and may loop according to header/interval controls.
- Timestamp get packets persist SDMA or global timestamp values to 8-byte-aligned memory destinations.
- Trap packets trigger interrupt-visible context state.
- `GPUVM_INV` and `GCR_REQ` alter GPU cache/TLB/translation state and can clear or log protection-fault status.
- AQL copy and barrier packets use completion-signal fields at dwords 14-15, integrating with queue-visible synchronization state.

Because helpers silently mask high bits, incorrectly sized values may be truncated rather than rejected at compile time or runtime.

## Dependencies And Integration Points

- Depends on SDMA v7.1.0 hardware packet definitions matching the generated macro layout exactly.
- Uses opcode/sub-op constants defined earlier in the same header, including `SDMA_OP_POLL_REGMEM`, `SDMA_OP_ATOMIC`, `SDMA_OP_TIMESTAMP`, `SDMA_OP_TRAP`, `SDMA_OP_GPUVM_INV`, `SDMA_OP_GCR_REQ`, `HEADER_AGENT_DISPATCH`, `HEADER_BARRIER`, `SDMA_OP_AQL_COPY`, and `SDMA_OP_AQL_BARRIER_OR`.
- `SDMA_PKT_GCR_REQ` integrates with the top-of-file `SDMA_GCR_*` helper macros for cache invalidation/writeback control.
- Native packet macros are intended for AMDGPU SDMA ring emitters; AQL macros integrate with AQL/HSA-style dispatch packets and completion signals.
- Address fields integrate with GPUVM, memory manager, fence, and scheduler code that provides GPU virtual/physical addresses, VMIDs, cache policy choices, and synchronization addresses.

## Risks And Edge Cases

- Macro arguments are evaluated once in the generated expression, but there is no type checking and no assertion that the input fits the mask. Overflow is truncated.
- Several fields encode shifted address slices (`addr_31_2`, `addr_31_4`, `write_addr_31_3`, `base_va_31_7`, page VA fields). Passing raw byte addresses without first shifting/extracting the expected slice can double-shift and generate invalid packets.
- Header fields share dword 0; callers must OR compatible fields and must not accidentally reuse mutually exclusive opcode/sub-op definitions.
- Reserved dwords and reserved header bits are exposed as macros in AQL sections; nonzero reserved values can break forward compatibility with firmware/hardware.
- Cache policy, CPV, TMZ, VMID, invalidation level bits, and GCR controls have hardware side effects. Incorrect values can lead to stale translations, incoherent memory, security-domain mistakes, or hard-to-debug GPU hangs.
- The AQL descriptors are 16 dwords and include reserved holes. Emitters must preserve exact packet size and zero reserved dwords when required by the queue ABI.
- `POLL_REGMEM` retry and interval fields are bounded to 16 and 12 bits respectively; long waits need higher-level loop policy.

## Test Signals

Good validation for this chunk is mostly structural and integration-level:

- Compile-test AMDGPU users of this header to catch renamed or missing macros.
- Unit or KUnit-style packet encoding tests can assert that representative macro ORs produce expected dword values, especially for shifted address fields and multi-field headers.
- Ring emission tests should verify packet lengths and dword offsets for poll/write, atomic, timestamp, GPUVM invalidation, GCR, NOP, and AQL packets.
- GPUVM stress tests should exercise `GPUVM_INV` and `GCR_REQ` after page-table updates and check for stale mappings or protection-fault logging regressions.
- Synchronization tests should cover timestamp writes, trap contexts, AQL completion signals, AQL barrier dependencies, and atomic loop behavior.
- Negative/static tests should flag nonzero reserved AQL dwords, unaligned timestamp destinations, and address values that exceed the macro field width before masking.
