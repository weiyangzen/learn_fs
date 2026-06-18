<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c

## Purpose
Generic SOF MMIO, mailbox, and firmware block memory helpers used by platform `snd_sof_dsp_ops` implementations that expose memory-mapped DSP resources.

## Important APIs, Types, and Functions
Exports `sof_io_write()`, `sof_io_read()`, `sof_io_write64()`, `sof_io_read64()`, `sof_mailbox_write()`, `sof_mailbox_read()`, `sof_block_write()`, and `sof_block_read()`. Block helpers use `snd_sof_dsp_get_bar_index()` to map firmware block types to SOF BAR indexes.

## Control Flow, State, and Persistence
Register helpers directly call `writel/readl/writeq/readq`. Mailbox helpers calculate addresses from `sdev->bar[sdev->mailbox_bar] + offset` and use `memcpy_toio/fromio`. `sof_block_write()` writes aligned 32-bit words via `__iowrite32_copy()` and handles trailing 1-3 bytes by read-modify-write of the final word; `sof_block_read()` copies from IO memory. No state is owned here; all addressing state is in `snd_sof_dev`.

## Dependencies and Integration
Depends on Linux IO accessors, non-atomic 64-bit IO helpers, SOF ops, and platform BAR mapping. Used by IPC mailboxes, firmware loaders, debug reads, and platform ops tables such as Tangier and HDA variants.

## Risks and Test Signals
Risks include unaligned trailing-byte source access in `sof_block_write()`, missing bounds checks against BAR sizes, endianness assumptions, and writeq availability on target architectures. Test signals are firmware memcpy loading with non-word-sized blocks, mailbox read/write validation, KASAN/UBSAN around trailing writes, and successful block reads from SRAM/debug regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/iomem-utils.c -->
