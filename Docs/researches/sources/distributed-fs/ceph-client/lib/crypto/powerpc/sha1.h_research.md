# sources/distributed-fs/ceph-client/lib/crypto/powerpc/sha1.h

## Purpose
Selects the PowerPC SHA-1 architecture implementation, either SPE multi-block compression under `CONFIG_SPE` or the regular PowerPC one-block transform otherwise.

## Important APIs, Types, and Functions
For SPE, declares `ppc_spe_sha1_transform`, defines `MAX_BYTES 2048`, `spe_begin`, `spe_end`, and multi-block `sha1_blocks`. For non-SPE, declares `powerpc_sha_transform` and defines a simple per-block `sha1_blocks` loop.

## Control Flow
In SPE builds, `sha1_blocks` chunks work into at most `MAX_BYTES / SHA1_BLOCK_SIZE` blocks per preemption-disabled SPE section, calls assembly, advances pointers, and repeats. In non-SPE builds, it calls `powerpc_sha_transform` once per block until all blocks are processed.

## State and Persistence
The SHA-1 state is mutated by the selected assembly transform. SPE begin/end temporarily disable preemption and enable kernel SPE state; no persistent globals are used.

## Dependencies and Integration Points
Includes PowerPC SPE switching and preemption headers. It is wired into the generic SHA-1 library by defining the architecture `sha1_blocks` helper.

## Risks
The SPE chunk size is chosen to limit preemption-off latency; changing it affects scheduler latency. Non-SPE one-block looping has more call overhead but simpler state handling. SHA-1 is not collision-resistant.

## Test Signals
Digest tests on SPE and non-SPE builds, plus large-buffer tests that cross the 2048-byte chunk boundary, validate both wrappers.
