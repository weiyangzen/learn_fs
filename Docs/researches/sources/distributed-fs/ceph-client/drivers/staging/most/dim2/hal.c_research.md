# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.c

## Purpose
Implements the low-level DIM2 hardware abstraction for MediaLB control table programming, DBR memory allocation, channel setup/teardown, buffer start/detach, interrupt servicing, MediaLB lock detection, and buffer-size normalization.

## Important APIs, Types, And Functions
Global `g` stores initialization state, MMIO base, fcnt, DBR allocation bitmap, and async-TX DBR accounting. DBR helpers allocate/free 16 KiB internal buffer RAM in fixed blocks. CTR helpers write/read CDT, ADT, MLB CAT, and AHB CAT entries through MADR/MDAT/MDWE. `dim2_configure_channel()` programs CDT/CAT/ADT and unmasks channel interrupts; `dim2_clear_channel()` reverses it. Async-TX DBR accounting tracks read/write pointer movement and remaining space. `dim_startup()`, `dim_shutdown()`, `dim_init_control()`, `dim_init_async()`, `dim_init_isoc()`, `dim_init_sync()`, `dim_destroy_channel()`, `dim_service_*()`, `dim_get_channel_state()`, `dim_enqueue_buffer()`, and `dim_detach_buffers()` form the exported HAL.

## Control Flow
Startup validates MMIO/clock/fcnt, clears hardware, configures MediaLB/HBI/DMA, and marks initialized. Channel init validates address/type sizes, allocates DBR, initializes software counters, and writes channel tables. Enqueue validates size and two-entry hardware queue depth, writes ADT entries for the next index, updates async DBR accounting, and toggles producer index. IRQ service clears hardware done flags, advances request counters, and task-context service converts requests into software done-buffer counts. Detach decrements done-buffer counts after the upper layer removes MBOs.

## State And Persistence
All state is volatile in static global `g` and `struct dim_channel`. Hardware table/register state is reset on startup/shutdown and channel destroy. No persistent storage.

## Dependencies And Integration Points
Depends on MMIO accessors, local register/error definitions, and the external `dimcb_on_error()` callback supplied by `dim2.c`. The caller must serialize access; `dim2.c` does this with `dim_lock`.

## Risks And Test Signals
The HAL uses a single static global, so only one DIM2 instance is safe. `dim2_transfer_madr()` busy-waits without timeout. DBR allocation/accounting and two-buffer queue state are high-risk. Test signals include startup/shutdown, concurrent channel init/destroy under lock, DBR allocation/free reuse, async TX DBR space accounting as RPC advances, underflow/overflow error paths, and interrupt service with multiple active channels.
