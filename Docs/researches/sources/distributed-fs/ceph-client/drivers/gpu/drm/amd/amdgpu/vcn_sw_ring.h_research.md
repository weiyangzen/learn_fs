# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_sw_ring.h

## Purpose

`vcn_sw_ring.h` declares the VCN decode software-ring emitter interface and its expected frame size. It provides a small shared contract for generation-specific VCN code that wants to use the `VCN_DEC_SW_CMD_*` packet protocol.

## Important APIs, Types, And Functions

`VCN_SW_RING_EMIT_FRAME_SIZE` describes the frame overhead as VM flush, two VM fences, and an end packet. The header declares emitters for fences, IBs, register waits, VM flushes, register writes, and end packets. The function signatures expose AMDGPU ring, job, and IB types but leave their definitions to included AMDGPU headers.

## Control Flow

The header has no runtime control flow. It establishes the compile-time contract used by ring function tables and the implementation in `vcn_sw_ring.c`.

## State And Persistence

No state is stored here. The macro is a derived constant that must stay synchronized with the implementation's emitted dword counts.

## Dependencies And Integration Points

It integrates with AMDGPU VCN ring setup and depends on existing definitions of `struct amdgpu_ring`, `struct amdgpu_job`, `struct amdgpu_ib`, `u64`, and `uint32_t`. It is included by `vcn_sw_ring.c` and any generation file that installs these emitters into a ring function table.

## Risks And Test Signals

Risk is mainly contract drift: if `VCN_SW_RING_EMIT_FRAME_SIZE` no longer matches the actual emitter dword count, callers may under-allocate ring space. Test signals are compile coverage and runtime ring tests that exercise VM flush plus fences without ring overflow.
