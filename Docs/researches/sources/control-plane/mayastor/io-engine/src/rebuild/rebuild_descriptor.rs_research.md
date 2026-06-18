# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_descriptor.rs

## Purpose
This file owns the common data-plane descriptor for rebuild copying. It opens source and destination bdevs, validates range compatibility, allocates DMA buffers, reads source segments, writes destination segments, and optionally verifies copied data.

## Important APIs, Types, And Functions
`RebuildDescriptor::new` opens bdevs from URIs and computes block/range/segment metadata. `validate` checks ranges and block-size compatibility. `validate_map` validates bitmap coverage. `get_segment_size_blks`, `dma_malloc`, `src_io_handle`, `dst_io_handle`, and `adjusted_iov` support task execution. `read_src_segment`, `write_dst_segment`, `verify_segment`, and `verify_failure` implement I/O.

## Control Flow
Construction resolves bdev names from URIs, opens source read-only and destination writable, rejects identical devices, gets nonblocking I/O handles, chooses a full destination range when none is supplied, validates both devices, and records start time. Copy tasks request an adjusted iovec, read the source, skip writes on NVMe unwritten-block status, write destination data, and verify if configured. Compare failures are ignored, converted to rebuild failure, or panic depending on `RebuildVerifyMode`.

## State, Persistence, And Dependencies
The descriptor keeps source/destination descriptors and handles open for the job lifetime. Persistent state is only the destination data written by I/O. Dependencies include `device_open`, bdev URI parsing, SPDK DMA buffers and NVMe statuses, core block-device traits, read options, and rebuild options/errors.

## Integration Points
Every rebuild backend delegates actual copy I/O to this descriptor, either directly or through wrappers like `NexusRebuildDescriptor` and `PartialSeqCopier`. Stats use descriptor block size, range, segment size, and start time.

## Risks
The current validation assumes equal block size and TODOs label/data partition protection. `adjusted_iov` asserts the buffer is large enough, so unexpected segment sizing can panic. Verification rereads the source after writing, which can report false mismatches if the source changes outside nexus range-lock protection. Unwritten source blocks skip destination writes and rely on destination state semantics being acceptable.

## Test Signals
Test invalid URI, missing bdev, same bdev, mismatched block size, out-of-range rebuild ranges, partial final segment sizing, unwritten-block read skip, write errors, verify compare modes, and DMA allocation alignment.
