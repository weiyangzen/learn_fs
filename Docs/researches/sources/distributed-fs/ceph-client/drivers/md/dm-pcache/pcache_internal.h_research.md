# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/pcache_internal.h

## Purpose
Provides shared low-level helpers for `dm-pcache`: logging macros, size constants, metadata header layout, CRC calculation, sequence comparison, and mirrored metadata-slot selection. It is the common persistence integrity layer used by superblock/cache-info/segment metadata code.

## Important APIs, Types, And Functions
`struct pcache_meta_header` stores a CRC, 8-bit sequence number, version byte, and reserved field at the start of pcache metadata records. `pcache_meta_crc()` computes CRC32C over a metadata object excluding the CRC field. `pcache_meta_seq_after()` compares 8-bit sequence numbers using signed wraparound arithmetic. `pcache_meta_find_latest()` scans `PCACHE_META_INDEX_MAX` copies, rejects CRC failures, selects the latest valid sequence, and copies the winning record into a caller buffer.

The file defines `PCACHE_KB`, `PCACHE_MB`, `PCACHE_META_INDEX_MAX`, and `PCACHE_CRC_SEED`, plus `pcache_err/info/debug` macros that include function and line.

## Control Flow
Callers pass the address of the first metadata header, the actual metadata size, the slot stride, and a destination buffer to `pcache_meta_find_latest()`. The helper uses `copy_mc_to_kernel()` for each slot so pmem machine-check faults are converted to `-EIO`. After choosing the newest valid slot it copies that slot into the destination and returns the source address; callers derive the active slot index from that address.

## State And Persistence
This header defines the persistent metadata envelope but stores no state itself. Its design assumes two alternating metadata slots, each independently checksummed and sequenced. Crash recovery can tolerate one torn slot if the other slot remains valid.

## Dependencies And Integration Points
It depends on Linux delay and CRC32C helpers and on pmem-safe copying through `copy_mc_to_kernel()`. Segment metadata, cache-device superblocks/cache-info, cache-tail positions, and segment generation records all use this contract. The logging macros are reused across the pcache implementation.

## Risks
The sequence comparison works only within half the 8-bit sequence space; if metadata updates wrap far enough between reads, latest-slot selection can become ambiguous. `pcache_meta_crc()` assumes the CRC field is the first four bytes and the caller supplies the exact object size. Any new metadata record that does not embed `pcache_meta_header` first will silently compute the wrong checksum.

## Test Signals
Unit-style tests should cover CRC rejection, single-slot corruption, sequence wraparound near 255-to-0, machine-check copy failure handling, and records where slot stride is larger than record size. Integration tests should verify that pcache reload chooses the latest metadata copy after simulated torn writes.
