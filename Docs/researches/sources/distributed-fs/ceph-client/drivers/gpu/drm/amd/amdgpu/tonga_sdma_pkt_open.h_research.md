# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_sdma_pkt_open.h

## Purpose

This generated-style header is the packet layout contract for Tonga-era SDMA command streams. It defines SDMA operation and sub-operation IDs plus bit masks, shifts, dword offsets, and helper macros used by ring emitters to pack packet fields into 32-bit command words.

## Important APIs, Types, and Functions

There are no functions or runtime types. The public API is macro-only: `SDMA_OP_*` opcodes, `SDMA_SUBOP_*` selectors, base header helpers such as `SDMA_PKT_HEADER_OP()`, and packet-specific helpers for copy, write, indirect buffer, semaphore, fence, SRBM write, pre-execute, conditional execute, constant fill, poll reg/mem, atomic, timestamp, trap, and nop packets.

## Control Flow

The file has no executable control flow. Consumers build SDMA packets by writing dwords in the documented order: header at dword 0, then address, count, geometry, tiling, mask, data, or synchronization fields depending on packet family.

## State and Persistence Behavior

The header persists no state. It describes command stream state that becomes persistent only after another driver component places the packed dwords into an SDMA ring or indirect buffer.

## Dependencies and Integration Points

The file is self-contained apart from the include guard. It integrates with AMDGPU SDMA ring code that emits hardware command buffers and must match the Tonga SDMA packet ABI.

## Risks

The macros mask input values but do not validate ranges, alignment, packet length, ordering, or mutually exclusive fields. A wrong field definition can corrupt GPU memory, hang a ring, or silently misprogram synchronization.

## Test Signals

Primary signals are successful SDMA ring tests, IB submission tests, copy/fill correctness, fence and semaphore completion, VM fault absence, and no ring timeout under tiled/linear copy paths.
