# sources/distributed-fs/ceph-client/drivers/scsi/arm/arm_scsi.h

## Purpose

`arm_scsi.h` provides shared command-private scatterlist pointer helpers for the ARM SCSI drivers. It adapts modern `struct scsi_cmnd` scatter-gather state into the older `struct scsi_pointer` style used by the Acorn and FAS216 state machines.

## Important APIs, Types, and Functions

`struct arm_cmd_priv` wraps a `struct scsi_pointer` for SCSI command private storage. `arm_scsi_pointer(cmd)` returns the per-command pointer. `init_SCp()` initializes that pointer from `scsi_sglist()`, `scsi_sg_count()`, and `scsi_bufflen()`. `next_SCp()` advances to the next scatterlist entry. `get_next_SCp_byte()` and `put_next_SCp_byte()` transfer one byte through the current pointer. `copy_SCp_to_sg()` copies the current pointer plus remaining chained SG entries into a caller-provided contiguous SG array for ISA-style DMA setup.

## Control Flow

Callers invoke `init_SCp()` when queueing a command. Transfer engines consume or update the returned pointer as data is moved. DMA-capable card wrappers use `copy_SCp_to_sg()` to hand an aligned SG array to platform DMA APIs. `BELT_AND_BRACES` validation recomputes total SG length and clamps `phase` if `scsi_bufflen()` disagrees with actual SG lengths.

## State and Persistence Behavior

All state is command-private and in-memory. The active fields are the current SG entry, current virtual pointer, residual length in this segment, number of remaining segments, and total transfer phase count. No data is persisted outside the command lifetime.

## Dependencies and Integration Points

This header depends on Linux scatterlist and SCSI command APIs. It is used by `acornscsi.c`, `fas216.h`/`fas216.c`, and FAS216 card wrappers that need to map command buffers to legacy DMA controllers.

## Risks and Edge Cases

`copy_SCp_to_sg()` has a `BUG_ON(bufs + 1 > max)`, so callers must size fixed SG arrays correctly. The helpers use `sg_virt()` and direct byte dereferences, so they assume CPU-accessible SG memory. The length mismatch fallback is intentionally naive and logs a warning rather than failing the command. `get_next_SCp_byte()` and `put_next_SCp_byte()` do not advance to the next SG entry on their own.

## Test Signals

Tests should cover zero-length commands, single and multiple SG entries, SG count at the fixed array limit, mismatched `scsi_bufflen()` versus SG total length, and bytewise PIO crossing segment boundaries via caller-managed `next_SCp()`.
