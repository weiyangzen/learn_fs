# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-packet.h

## Purpose
`cvmx-packet.h` defines the Octeon packet buffer pointer format used by hardware and executive packet helpers. It is intentionally small: the core export is `union cvmx_buf_ptr`, a 64-bit descriptor that can be viewed as an opaque pointer, raw integer, or named hardware fields.

## Important APIs, Types, and Constants
- `union cvmx_buf_ptr` exposes `void *ptr`, `uint64_t u64`, and the field view `s.i`, `s.back`, `s.pool`, `s.size`, and `s.addr`.
- `addr` is a 40-bit pointer to the first byte of packet data, not necessarily the allocation base.
- `size` is a 16-bit segment length in bytes.
- `pool` identifies the hardware memory pool for recycle/free behavior.
- `back` records how far to step back, in cache-line units, to find the actual buffer start.
- `i` inverts the packet free decision and is documented as cleared by hardware for inbound packets.

## Control Flow
The header has no functions. Runtime behavior is in consumers that receive or build packet descriptors, inspect or update the union fields, and pass raw `u64` values to hardware queues.

## State and Persistence Behavior
The union describes transient packet-buffer metadata held in descriptors, work-queue entries, and packet processing state. It does not persist data itself, but wrong field interpretation affects buffer ownership and memory-pool recycling.

## Dependencies and Integration Points
- Depends on fixed-width integer types and the surrounding `__BIG_ENDIAN_BITFIELD` definition.
- Used by Octeon executive packet code; repository call sites include `arch/mips/cavium-octeon/executive/cvmx-helper.c`, where `union cvmx_buf_ptr` values are used while setting up packet buffers.
- Integrates with FPA/pool management, packet input hardware, and packet output paths that expect the exact 64-bit layout.

## Risks
- The `void *ptr` view and 40-bit `addr` field are not interchangeable on every virtual/physical address path. Treating a descriptor address as a normal kernel virtual pointer can corrupt memory or fail on high address bits.
- Endian bitfield ordering is critical for descriptors produced by hardware.
- Miscomputing `back`, `pool`, or `size` can leak buffers, return them to the wrong pool, or make packet data overlap metadata.

## Test Signals
- Packet input/output smoke tests should validate that received descriptors point to valid data and that recycled buffers return to the expected pool.
- Memory leak or double-free symptoms in Octeon packet paths are strong signals of `cvmx_buf_ptr` layout or ownership regressions.
- Build-time checks should include both C users that rely on `u64` and those that access `s.*` fields.
