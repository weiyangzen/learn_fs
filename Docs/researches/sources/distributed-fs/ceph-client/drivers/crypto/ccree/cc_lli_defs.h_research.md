# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_lli_defs.h

## Purpose

`cc_lli_defs.h` defines CryptoCell linked-list item layout and limits for MLLI scatter/gather tables. It supports buffer manager code that converts Linux scatterlists into hardware-readable DMA list entries.

## Important APIs, Types, And Functions

Constants define descriptor DLLI size width, maximum MLLI entry size (`0xffff`), maximum data and associated-data entries, table alignment, maximum buffer groups, total entry budget, and the two-word LLI layout. Word 0 stores low address bits. Word 1 stores 16 bits of size and, on 64-bit DMA builds, 16 high address bits. Inline setters `cc_lli_set_addr()` and `cc_lli_set_size()` pack those fields using masks and `FIELD_PREP`.

## Control Flow

The header has no independent control flow. Buffer mapping code allocates MLLI tables, iterates scatterlist segments, writes each entry with these helpers, and then references the MLLI table from hardware descriptors.

## State And Persistence Behavior

LLI entries are transient DMA-visible memory. They persist only for the lifetime of the mapped crypto request and are unmapped or reused by buffer manager cleanup.

## Dependencies And Integration Points

The file depends on Linux types, DMA address width configuration, `GENMASK`, and `FIELD_PREP`. It integrates with `cc_buffer_mgr` and descriptor flows that use `DMA_MLLI` in `cc_hw_queue_defs.h`.

## Risks And Edge Cases

Each MLLI entry size is 16-bit, so larger scatterlist chunks must be split before encoding. Tables must be 32-bit aligned. On 64-bit DMA, only 16 high address bits are encoded, matching a 48-bit address assumption. Exceeding entry-count limits can corrupt adjacent MLLI workspace or force request mapping failure.

## Test Signals

Scatterlist-heavy hash, cipher, and AEAD tests should force MLLI paths. DMA API debugging and IOMMU tests with high physical addresses validate address packing. Large fragmented inputs should either succeed with split entries or fail cleanly before descriptor submission.
