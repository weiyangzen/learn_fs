# sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.c

### Purpose
`mvsdio.c` is the Marvell Orion SDIO/MMC/SD host driver. It drives a register interface described by `mvsdio.h`, supports one-fragment DMA or PIO fallback, handles controller-specific FIFO quirks, programs Marvell MBUS DRAM windows, provides SDIO card interrupt delivery, and exposes basic clock/power/bus-width control to the MMC core.

### Important APIs, Types, And Functions
The core state is `struct mvsd_host`, with MMIO base, current request, spinlock, cached transfer mode/interrupt/host-control registers, PIO buffer state, SG fragment count, clock timing, timeout timer, MMC host, device, and clock. MMC callbacks in `mvsd_ops` are `mvsd_request()`, `mvsd_set_ios()`, `mvsd_enable_sdio_irq()`, and GPIO write-protect. Major helpers are `mvsd_setup_data()`, `mvsd_finish_cmd()`, `mvsd_finish_data()`, `mvsd_irq()`, `mvsd_timeout_timer()`, `mvsd_power_up()`, `mvsd_power_down()`, and `mv_conf_mbus_windows()`.

### Control Flow
Probe requires DT, gets IRQ and clock, allocates the host, sets MMC limits, derives `base_clock`, parses MMC properties, maps registers, optionally programs MBUS windows from `mv_mbus_dram_info()`, powers the controller down, requests the IRQ, initializes the timeout timer, and registers the host. A request builds command, transfer, and interrupt masks, configures data if present, selects PIO when forced or when block size/SG offset/write alignment is unsafe for DMA, writes argument and command registers, enables normal/error interrupts, and arms a timer using command busy timeout or 5 seconds. IRQ first services PIO FIFO RX/TX events, then on command/data/auto-CMD/error completion disables interrupts, deletes the timer, finishes command and data, and completes the MMC request. The timer resets hardware and completes the request with timeout if no expected interrupt arrives.

### State, Persistence, And Dependencies
Runtime state is the current request plus cached `xfer_mode`, `intr_en`, `ctrl`, PIO pointer/size, SG DMA fragment count, `ns_per_clk`, and current clock. Hardware state includes block size/count, DMA address registers, argument/command, transfer mode, host-control timeout/bus mode, clock divisor, interrupt status/enables, reset, and optional MBUS remap windows. Dependencies include MMC core, clock framework, platform DT, Marvell MBUS helpers, DMA mapping, timers, unaligned access helpers, and register definitions from `mvsdio.h`. Module parameters `maxfreq` and `nodma` alter max clock and DMA usage.

### Integration Points
The OF compatible is `"marvell,orion-sdio"`. The driver uses GPIO helpers for write-protect and card-detect behavior parsed by `mmc_of_parse()`, but SDIO card interrupts are controller-native via `MVSD_NOR_CARD_INT`. MBUS window programming connects the controller DMA master to system DRAM. The MMC core sees `max_segs = 1`, large single-segment request limits, and controller-supported 3.2-3.4 V OCR.

### Risks
DMA is limited and alignment-sensitive: unaligned block sizes, unaligned offsets, and host-to-card buffers not 64-byte aligned fall back to PIO. `mvsd_setup_data()` maps only one SG address into hardware despite recording mapped fragments, consistent with `max_segs = 1`; violating that limit would be dangerous. FIFO behavior has documented quirks: FIFO_EMPTY may lag after unusual block sizes, RX FIFO 8-word status misses exactly-32-byte tails, and TX_FIFO_8W is unreliable. The timeout path calls finish helpers after reset while holding/releasing locks carefully; races with a late IRQ are possible. High-speed enable is disabled by `#if 0` due card compatibility problems, so performance expectations should account for that.

### Test Signals
Test PIO and DMA transfer paths, forced `nodma`, unaligned buffers and odd block sizes, exact 32-byte RX tails, small TX tails, multi-block with auto-CMD12, SDIO card interrupts, timeout recovery, MBUS window programming on Marvell platforms, module `maxfreq`, clock off/on transitions, and card-detect/write-protect integration. Fault injection should include command CRC/timeout, data CRC/timeout, auto-CMD12 errors, and late/spurious interrupts after masks are disabled.
