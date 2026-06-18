# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.c

## Purpose
This file implements Linux-specific HPI OS services for delays and coherent DMA memory allocation.

## Important APIs, Types, And Functions
It defines `hpios_delay_micro_seconds()`, `hpios_locked_mem_alloc()`, and `hpios_locked_mem_free()`. The DMA routines operate on `struct consistent_dma_area` from `hpios.h`.

## Control Flow
Delay selection uses `schedule_timeout_uninterruptible()` for longer sleeps when not in interrupt context, `udelay()` for up to 2000 microseconds, and `mdelay()` for longer interrupt-context delays. DMA allocation calls `dma_alloc_coherent()`, records virtual address, DMA handle, device, and size on success, and clears size on failure. Free only releases memory when size is nonzero.

## State, Persistence, And Dependencies
No global state is stored. Allocated DMA state persists in the caller-provided `consistent_dma_area`. Dependencies include Linux delay, scheduler, DMA mapping through included HPI internals, and HPI debug logging.

## Integration Points
Hardware-specific HPI code uses these wrappers to sleep/poll safely and allocate bus-master buffers without embedding Linux APIs throughout firmware-facing code.

## Risks
Long interrupt-context delays fall back to busy `mdelay()`, which can hurt latency. Physical addresses are later narrowed to `u32` by the inline getter in the header, so platforms requiring wider DMA addresses need scrutiny. Free returns error on double-free but leaves stale pointers.

## Test Signals
Signals include successful coherent allocation/free, failed allocation reporting size zero, no scheduling while in interrupt context, and DMA address compatibility with supported adapters.
