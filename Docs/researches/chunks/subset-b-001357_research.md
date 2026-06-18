# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0_0_pkt_open.h lines 4514-5672

## Purpose

This chunk is the final portion of the generated/open SDMA v6.0.0 packet-layout header used by AMDGPU SDMA code. It does not implement runtime control flow itself; instead, it defines the dword offsets, bit masks, shifts, and field-packing macros that SDMA ring emitters use to construct command packets consumed by the SDMA firmware/hardware command processor.

The covered range starts in the middle of `SDMA_PKT_POLL_REGMEM`, then defines complete layouts for register/memory polling variants, atomic operations, timestamp packets, trap packets, GPUVM invalidation, global cache-request packets, NOP packets, and AQL-format SDMA packets. The file ends with the include guard close. These macros are part of the ABI between driver ring writes and the SDMA engine, so their main purpose is encoding accuracy rather than local computation.

## Important APIs, Types, And Functions

There are no C functions or types in this chunk. The important API surface is a set of preprocessor macros with a uniform pattern:

- `<PACKET>_<WORD>_<field>_offset`: dword index of the word in the packet.
- `<PACKET>_<WORD>_<field>_mask`: unshifted bit mask for the field value.
- `<PACKET>_<WORD>_<field>_shift`: bit position within the target dword.
- `<PACKET>_<WORD>_<FIELD>(x)`: packer that masks `x` and shifts it into command-word position.

The packet groups covered here are:

- `SDMA_PKT_POLL_REGMEM`: tail fields for 64-bit poll address, compare value, mask, interval, and retry count.
- `SDMA_PKT_POLL_REG_WRITE_MEM`: header fields plus a register source address and 64-bit memory destination address.
- `SDMA_PKT_POLL_DBIT_WRITE_MEM`: header fields plus destination address, start page, and page count for dirty-bit/page-state style memory writes.
- `SDMA_PKT_POLL_MEM_VERIFY`: header, pattern, two compare address ranges, record-address fields, and a reserved word.
- `SDMA_PKT_ATOMIC`: header fields for `loop`, `tmz`, cache policy, `cpv`, and `atomic_op`, followed by target address, source data, compare data, and loop interval words.
- `SDMA_PKT_TIMESTAMP_SET`, `SDMA_PKT_TIMESTAMP_GET`, and `SDMA_PKT_TIMESTAMP_GET_GLOBAL`: timestamp initialization or timestamp writeback layouts.
- `SDMA_PKT_TRAP` and `SDMA_PKT_DUMMY_TRAP`: trap headers plus interrupt-context payload.
- `SDMA_PKT_GPUVM_INV`: VM invalidation request payload fields for VMID request bits, flush type, L2/L1/PDE/PT invalidation controls, fault-status clearing, logging, 4 KiB mode, and page VA fragments.
- `SDMA_PKT_GCR_REQ`: global cache request payload fields for base/limit VA, GCR control bits, and VMID.
- `SDMA_PKT_NOP`: header operation/suboperation/count fields and optional data word.
- `SDMA_AQL_PKT_HEADER`, `SDMA_AQL_PKT_COPY_LINEAR`, and `SDMA_AQL_PKT_BARRIER_OR`: AQL packet header fields, copy-linear payload, dependent barrier addresses, per-dependent-address cache policies, and completion-signal fields.

## Control Flow

This header contributes to control flow indirectly through command streams. Driver code writes dwords into an SDMA ring or IB; each macro packs one field into the dword that SDMA firmware later decodes. For example, `sdma_v7_0.c` includes this header and uses `SDMA_PKT_NOP_HEADER_COUNT()`, `SDMA_PKT_GCR_REQ_PAYLOAD*()`, `SDMA_PKT_POLL_REGMEM_*()`, and `SDMA_PKT_TRAP_INT_CONTEXT_INT_CONTEXT()` while emitting ring padding, cache requests, register/memory polls, and traps.

The implied packet construction flow is:

1. Emit a header word by ORing the packet `OP()` macro with sub-operation and policy macros where required.
2. Emit payload dwords at the offsets documented by the `_offset` macros.
3. Split 64-bit addresses or data into low and high dwords using the corresponding `*_LO` and `*_HI` macros.
4. For shared dwords, OR non-overlapping field macros, such as `INTERVAL()` with `RETRY_COUNT()` or GCR control bits with address fragments.
5. Submit the ring/IB to hardware, where the packet processor interprets the encoded dwords.

Because the chunk is macro-only, there are no branches, loops, locks, error paths, allocations, or return values inside the source range itself. All runtime sequencing and validation belongs to the caller that emits the SDMA packets.

## State And Persistence Behavior

The macros are compile-time constants and stateless inline expressions. They do not read or mutate driver state, hardware registers, memory buffers, or persistent files.

The state effects happen when callers use the encoded packets. The packet families in this chunk can cause SDMA-visible effects such as polling memory/register state, writing memory, performing atomic memory operations, setting or capturing timestamps, generating traps, invalidating GPUVM/TLB state, issuing global cache operations, padding command streams, copying memory through AQL packets, and signaling AQL completion addresses. Reserved-word macros allow callers to explicitly emit reserved dwords, which should usually be zero unless hardware documentation requires another value.

The header definitions persist only as build artifacts in compiled driver code. If a macro value is wrong, every compiled packet emitter using that macro can persistently emit malformed command streams until the driver is rebuilt.

## Dependencies

This chunk depends on the packet opcode and subopcode constants defined earlier in the same header, such as `SDMA_OP_POLL_REGMEM`, `SDMA_OP_ATOMIC`, `SDMA_OP_TIMESTAMP`, `SDMA_OP_TRAP`, `SDMA_OP_GPUVM_INV`, `SDMA_OP_GCR_REQ`, `SDMA_OP_NOP`, `SDMA_SUBOP_POLL_REG_WRITE_MEM`, `SDMA_SUBOP_POLL_DBIT_WRITE_MEM`, `SDMA_SUBOP_POLL_MEM_VERIFY`, and the AQL header/op constants.

The downstream dependencies are the SDMA ring emitters and scheduler paths that include this header through SDMA generation-specific C files. In this tree, `sdma_v7_0.c` includes `sdma_v6_0_0_pkt_open.h` and uses a subset of these macros for NOP padding, polling waits, GCR requests, and traps. Other packet definitions in the chunk are available for queue management, memory operations, VM invalidation, or AQL/user-queue paths even when not all are referenced in the local file search.

The macros also depend on hardware documentation for SDMA v6 packet formats. The driver cannot infer correctness at runtime; field widths such as 30-bit register source addresses, 29-bit timestamp writeback addresses shifted by 3, 31-bit page VA slices, 13-bit atomic loop intervals, 22-bit AQL copy counts, and 5 packed AQL barrier cache-policy fields must match SDMA firmware expectations exactly.

## Integration Points

The immediate integration point is command emission into `struct amdgpu_ring` or IB buffers through helpers such as `amdgpu_ring_write()`. Callers compose these macros with opcode constants, register addresses, GPU virtual/physical addresses, VMID values, cache policy values, and synchronization flags.

Specific integration surfaces include:

- Ring padding and no-op insertion through `SDMA_PKT_NOP_HEADER_*`, including count-based NOP packets.
- Fence and synchronization waits through the earlier `SDMA_PKT_POLL_REGMEM` header fields plus this chunk's address, value, mask, retry, and interval fields.
- Register-to-memory or dirty-bit/status writeback workflows through `POLL_REG_WRITE_MEM` and `POLL_DBIT_WRITE_MEM`.
- Timestamp initialization/writeback paths through `TIMESTAMP_SET`, `TIMESTAMP_GET`, and `TIMESTAMP_GET_GLOBAL`.
- Interrupt or test signaling through `TRAP` and `DUMMY_TRAP` interrupt-context fields.
- VM and cache maintenance through `GPUVM_INV` and `GCR_REQ` payload macros.
- Atomic memory operations through `SDMA_PKT_ATOMIC`, including compare-and-loop forms controlled by `loop`, compare data, and loop interval.
- AQL/HSA-style SDMA dispatch through `SDMA_AQL_PKT_HEADER`, `SDMA_AQL_PKT_COPY_LINEAR`, and `SDMA_AQL_PKT_BARRIER_OR`, including completion-signal addresses used by user-mode or MES/user-queue style workflows.

## Risks And Edge Cases

- The packer macros mask inputs but do not validate semantic range. Oversized values are silently truncated, which can turn a bad address, VMID, count, retry value, cache policy, or atomic operation into a valid-looking but wrong packet.
- Several macros encode pre-shifted address fragments. Callers must pass the field value expected by the macro, not always the raw byte address. Examples include `SRC_ADDR_addr_31_2`, timestamp `write_addr_31_3`, `START_PAGE_addr_31_4`, `GPUVM_INV` page VA slices, and GCR base/limit VA slices.
- Shared dwords rely on non-overlapping masks and correct OR composition. A caller that writes fields separately instead of ORing them into one dword can drop fields such as retry/interval, GCR control/address fragments, or AQL header fence scopes.
- Reserved fields and reserved dwords should be emitted according to hardware requirements. Nonzero reserved bits may be rejected by firmware or produce undefined hardware behavior.
- The `SDMA_PKT_POLL_REGMEM_DW5_retry_count_mask` is `0x00000FFF` with shift 16, so retry counts beyond 12 bits are truncated. Poll packets can either time out too early or poll unexpectedly long if callers miscompute this field.
- `SDMA_PKT_ATOMIC_HEADER_ATOMIC_OP()` exposes only seven bits. Any mismatch between software atomic-op enums and hardware encodings can cause incorrect memory operations.
- `SDMA_AQL_PKT_COPY_LINEAR_COUNT()` exposes a 22-bit count, while non-AQL copy packet layouts elsewhere in the file have different count widths. Reusing the wrong macro family can corrupt packet length semantics.
- `SDMA_AQL_PKT_BARRIER_OR_CACHE_POLICY*()` packs five 3-bit policies with gaps between fields. Callers must choose the matching policy field for each dependent address and must not assume a dense array encoding.
- The header is generation-specific but is included by `sdma_v7_0.c` in this tree. Any SDMA v7 reuse is deliberate only if packet layouts are compatible; future ASIC changes need review before reusing these constants.

## Test Signals

- Build coverage should compile SDMA generation files that include this header, especially `sdma_v7_0.c`, with no macro-name drift or missing packet-field definitions.
- Ring self-tests should pass for SDMA queues and exercise NOP padding, fence polling, trap emission, and IB submission paths that consume these macros.
- VM and memory-management tests should cover `SDMA_PKT_GCR_REQ` and `SDMA_PKT_GPUVM_INV` encodings by validating TLB/cache invalidation behavior under VM bind/unbind, page-table update, and recovery workloads.
- Fence/poll timeout tests should verify that `SDMA_PKT_POLL_REGMEM_DW5_INTERVAL()` and `RETRY_COUNT()` produce expected wait behavior and do not hang rings.
- Timestamp tests should verify 64-bit timestamp set/get/global writebacks at correctly aligned addresses.
- Atomic-operation tests should cover source data, compare data, loop enable, loop interval, TMZ, and cache-policy combinations on supported hardware.
- AQL user-queue or MES tests should validate AQL copy-linear and barrier-or packets, including dependent-address waits and completion-signal writes.
- Static packet-layout checks can compare generated dword offsets, masks, and shifts against SDMA v6 hardware XML/spec sources and against adjacent generation headers such as `sdma_v7_1_0_pkt_open.h` to detect accidental drift.
