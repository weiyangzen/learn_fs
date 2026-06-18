# sources/distributed-fs/ceph-client/kernel/dma.c

## Purpose
This legacy file manages reservation of ISA-style DMA channels and exposes channel ownership through `/proc/dma` when procfs is enabled. It provides `request_dma()` and `free_dma()` for architectures that define `MAX_DMA_CHANNELS`, and harmless stubs otherwise.

## Important APIs, Types, And Functions
`DEFINE_SPINLOCK(dma_spin_lock)` exports the legacy DMA lock. `struct dma_chan` stores a busy flag and `device_id`. `request_dma()` reserves a channel with `xchg()`. `free_dma()` releases it and warns on invalid or double-free attempts. `proc_dma_show()` prints busy channels or `No DMA`. `proc_dma_init()` creates `/proc/dma`.

## Control Flow
With `MAX_DMA_CHANNELS`, channel 4 starts reserved as `cascade`. `request_dma()` rejects out-of-range channel numbers, atomically swaps the lock to busy, and records the device name. `free_dma()` validates range and atomically clears the busy flag. Procfs iteration prints every busy channel and associated owner. Without `MAX_DMA_CHANNELS`, requests fail with `-EINVAL` and frees are no-ops.

## State, Persistence, And Dependencies
State is the static `dma_chan_busy[]` array and exported `dma_spin_lock`. It is not persistent across boot. Dependencies include architecture `asm/dma.h`, procfs, seq_file, `xchg()`, and kernel warning/printk support.

## Integration Points
Legacy drivers call `request_dma()`/`free_dma()` directly. Procfs consumers read `/proc/dma`. The symbols are exported for modules.

## Risks
The `device_id` pointer is stored, not copied, so callers must pass storage that remains valid while the channel is reserved. `free_dma()` does not clear `device_id`, but proc output is gated by the busy flag. Drivers must follow the documented IRQ-then-DMA acquisition order to reduce resource deadlocks.

## Test Signals
Test valid reservation/free, duplicate reservation returning `-EBUSY`, out-of-range request returning `-EINVAL`, double free warning, channel 4 reserved by default, stub behavior on architectures without `MAX_DMA_CHANNELS`, and `/proc/dma` output.
