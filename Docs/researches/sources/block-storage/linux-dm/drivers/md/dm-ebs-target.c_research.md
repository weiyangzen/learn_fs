# File Research: sources/block-storage/linux-dm/drivers/md/dm-ebs-target.c

## Role
Implements the `ebs` target, which emulates a smaller logical block size on an underlying device with a larger native block size, for example 512-byte logical sectors on a 4 KiB-native device.

## Target Interface
- Constructor syntax is `<dev_path> <offset> <ebs> [<ubs>]`.
- `<ebs>` and optional `<ubs>` are block sizes in 512-byte sectors and must be powers of two.
- If `<ubs>` is omitted, it is derived from the lower device logical block size.
- The target rejects offsets not aligned to the underlying block size.

## Core Mechanics
- `struct ebs_c` stores the lower device, dm-bufio client, ordered workqueue, queued bio list, start sector, emulated block size, underlying block size, and sector-to-buffer block shift.
- A dm-bufio client is created using the underlying block size in bytes.
- Partial or overlapping bios are queued to `__ebs_process_bios()`, which uses bufio reads or new buffers to copy between bio pages and underlying-size blocks.
- Fully aligned bios bypass the workqueue and are remapped directly after forgetting any overlapping cached buffers.
- Discards are trimmed to complete underlying blocks only; partial first and last underlying blocks are not discarded.

## Read/Write Handling
- Reads copy bytes from bufio blocks into bio vectors and flush the page cache line state with `flush_dcache_page()`.
- Writes use read-modify-write when a bio only partially overwrites an underlying block and use `dm_bufio_new()` when a full block is overwritten.
- Dirty buffers are written before bio completion so `REQ_FUA` and `REQ_SYNC` semantics are preserved as far as this target can enforce them.
- Prefetching is used for reads and for misaligned write edge blocks.

## Status and Limits
- Table status emits `<dev> <start> <ebs>` or `<dev> <start> <ebs> <ubs>` depending on whether `<ubs>` was supplied.
- IO hints expose logical block size as `<ebs>` and physical block size as `<ubs>`.
- Flush and discard are enabled; secure erase, write same, and write zeroes are disabled.

## Important Invariants
- `to_bytes(ebs)` must fit in one page.
- Direct IO paths must drop relevant bufio cache state before remapping.
- The workqueue is ordered, serializing bufio-mediated read-modify-write sequences.

## Filesystem/Storage Relevance
This target lets upper layers and filesystems exercise smaller logical block sizes even when the lower device requires larger physical writes. It is especially relevant for testing filesystem behavior on 4K-native media with 512-byte emulation.

## Notable Risks
- Partial-block read-modify-write depends on bufio cache coherence with directly remapped aligned IO.
- The target is not a general transformation layer for all block operations; several write-like operations are explicitly disabled.
