# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1_pkt.h

## Purpose
`gfx_v12_1_pkt.h` defines PM4 packet constructors, packet decoders, opcode constants, and bitfield helper macros for GFX 12.1 command processor packets. `gfx_v12_1.c` uses these macros when emitting KIQ, compute, synchronization, fence, TLB invalidate, queue map/unmap, query status, register access, and memory coherency packets.

## Important APIs and macro groups
The base packet constructors are `PACKET0(reg, n)`, `PACKET2(v)`, `PACKET3(op, n)`, and `PACKET3_COMPUTE(op, n)`. Decode helpers are `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, and `CP_PACKET3_GET_OPCODE()`.

The opcode list covers common graphics and compute packet 3 commands, including dispatch/draw, `PACKET3_WRITE_DATA`, `PACKET3_WAIT_REG_MEM`, `PACKET3_INDIRECT_BUFFER`, `PACKET3_COPY_DATA`, `PACKET3_EVENT_WRITE`, `PACKET3_RELEASE_MEM`, `PACKET3_DMA_DATA`, `PACKET3_ACQUIRE_MEM`, register load/set packets, `PACKET3_INVALIDATE_TLBS`, `PACKET3_SET_RESOURCES`, `PACKET3_MAP_QUEUES`, `PACKET3_UNMAP_QUEUES`, and `PACKET3_QUERY_STATUS`.

Bitfield helpers are grouped by packet. Examples include `WRITE_DATA_DST_SEL`, `WR_CONFIRM`, XCD/MID scope and temporal fields; `WAIT_REG_MEM_FUNCTION`, memory/register space, operation, die ID, and temporal fields; `COPY_DATA_SRC_SEL` and destination/scope/temporal fields; release/acquire memory GCR controls; DMA data source/destination controls; queue resource, map, unmap, and query status controls; and TLB invalidate destination/PASID/flush fields.

## Control flow and integration
This header has no runtime control flow. It is included by `gfx_v12_1.c`, where packet macros become the low-level vocabulary for `amdgpu_ring_write()` sequences. The macros encode hardware ABI details directly into emitted command streams, so their consumers are sensitive to exact bit positions, packet lengths, and packet-specific comments.

KIQ queue management in `gfx_v12_1.c` uses `PACKET3_SET_RESOURCES`, `PACKET3_MAP_QUEUES`, `PACKET3_UNMAP_QUEUES`, and `PACKET3_QUERY_STATUS`. Ring tests and register access use `WRITE_DATA`, `COPY_DATA`, and `WAIT_REG_MEM`. Fence and cache synchronization use `RELEASE_MEM` and `ACQUIRE_MEM`. TLB invalidation uses `PACKET3_INVALIDATE_TLBS`.

## State and persistence behavior
The header owns no persistent state. Its macros produce immediate integer values embedded into ring buffers and indirect buffers. Once emitted, those values persist in GPU-visible command memory until consumed by the command processor or overwritten by ring reuse.

## Dependencies
The header depends on common AMDGPU register helper macro `REG_SET()` for `PACKET2(v)` and on consumers providing standard integer expressions. It shares opcode/bitfield contracts with GC 12.1 command processor firmware and hardware. Any mismatch between these definitions and firmware expectations directly affects command submission correctness.

## Risks and edge cases
Because these are preprocessor macros, type checking is minimal and argument side effects can be evaluated inside shifts. Field helpers generally mask inputs only when explicitly written to do so; several helpers shift raw values. Incorrect packet count arguments can desynchronize the command stream.

There are apparent macro-quality risks worth compile-testing carefully. `INDIRECT_BUFFER_TEMPORAL(x)` is written with mismatched parentheses, and `COPY_DATA_SRC_DST_REMOTE_MODE(x)` has precedence that may not match the intended `(((x) & 0x1) << 16)` shape. These may be unused today, but use by future code could cause compile failures or wrong packet fields. The header also contains typo/comment issues such as `DOOREBLL` in `PACKET3_RELEASE_MEM_ADD_DOOREBLL_OFFSET`, which is harmless if consumers use the exact macro name but can mislead readers.

The packet definitions are a hardware ABI surface. Reusing macros from another GFX generation, changing bit positions, or using graphics-only packet assumptions on compute/KIQ rings can lead to hangs, missed fences, failed TLB invalidation, or queue-management failures.

## Test signals
Primary validation is compile coverage of all used macros and runtime ring validation from `gfx_v12_1_ring_test_ring()` and `gfx_v12_1_ring_test_ib()`. Additional signals include successful KIQ map/unmap/query, fence completion, VM flush/TLB invalidation correctness, release/acquire memory coherency behavior, MES user queue fence IRQ handling, and lack of command processor hangs under suspend/resume and reset. Static analysis or targeted build tests should cover currently unused macros before they are adopted.
