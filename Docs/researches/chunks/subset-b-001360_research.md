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
