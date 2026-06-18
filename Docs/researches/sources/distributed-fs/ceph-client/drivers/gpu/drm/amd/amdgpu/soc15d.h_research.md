# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15d.h

## Purpose

`soc15d.h` is a command packet definition header for GFX9/SOC15 command submission and multimedia engines. It defines ring counts, PM4 packet type encoders/decoders, PACKET3 opcodes, bitfield helpers, compute queue management packet fields, cache/memory synchronization fields, TLB invalidation fields, and VCE/HEVC command identifiers.

## Important APIs, Types, And Functions

The core packet builders are `PACKET0()`, `PACKET2()`, `PACKET3()`, `PACKET3_COMPUTE()`, and `PACKETJ()`. Decoder helpers include `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, `CP_PACKET3_GET_OPCODE()`, and PACKETJ field extractors. The long PACKET3 section enumerates opcodes such as `WRITE_DATA`, `WAIT_REG_MEM`, `INDIRECT_BUFFER`, `COPY_DATA`, `EVENT_WRITE`, `RELEASE_MEM`, `ACQUIRE_MEM`, register load/set packets, `INVALIDATE_TLBS`, `SET_RESOURCES`, `MAP_QUEUES`, `UNMAP_QUEUES`, and `QUERY_STATUS`. Multimedia command constants cover VCE and HEVC encoder ring packets.

## Control Flow

There is no executable code. Runtime behavior is created by other modules composing command buffers with these macros. Those command buffers are consumed by GPU command processors, SDMA-related synchronization paths, compute queue management, graphics rings, KFD queue setup, or multimedia engines depending on packet type and opcode.

## State And Persistence Behavior

The header does not store state, but packet encodings built from it can program registers, update memory, emit fences, flush/invalidate caches and TLBs, map or unmap queues, and signal interrupts. Incorrect constants can corrupt command streams or persistent GPU context state.

## Dependencies, Risks, And Test Signals

The header depends on generic bit helpers such as `REG_SET()`/field-style shifts used throughout AMDGPU. It is tightly coupled to hardware packet ABI, so risks are silent command misencoding, wrong register aperture ranges, invalid cache policy bits, or queue management fields that break KFD. Tests include command submission on graphics/compute rings, IB chaining, fence signaling, cache flush and TLB invalidation validation, KFD queue map/unmap/preemption, VCE/HEVC ring tests, and parser tests that decode generated packet headers.
