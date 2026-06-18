# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.h

## Purpose

`dw_mmc.h` is the shared private interface for the Synopsys DesignWare MMC/SD/SDIO host controller driver family. It does not implement a platform driver itself; it defines the controller state object, common state-machine/event enums, DMA hooks, register offsets, bit definitions, FIFO access helpers, exported core entry points, and per-SoC extension callbacks consumed by DesignWare MMC core and platform-specific glue.

## Important APIs, Types, And Functions

- `enum dw_mci_state` models the bottom-half request state machine: idle, command send, data send, data busy, stop send, data error, CMD11 voltage-switch states.
- `enum dw_mci_cookie` tracks DMA mapping ownership for MMC requests: unmapped, pre-mapped by `pre_req`, and mapped by transfer preparation.
- `enum { TRANS_MODE_PIO, TRANS_MODE_IDMAC, TRANS_MODE_EDMAC }` identifies the selected transfer backend.
- `struct dw_mci_dma_slave` carries an external DMA channel and direction.
- `struct dw_mci` is the central host state. It holds MMIO pointers, current `mmc_request`/`mmc_command`/`mmc_data`, stop command storage, DMA buffers and ops, command/data status snapshots, workqueue/event bitmaps, clocks, reset controller, FIFO push/pull state, timers, quirks, IRQ metadata, slot/host references, and clock phase map.
- `struct dw_mci_dma_ops` defines the DMA backend contract: `init`, `start`, `complete`, `stop`, `cleanup`, and `exit`.
- `struct dw_mci_drv_data` is the variant hook table for capabilities, initialization, DT parsing, tuning, HS400 preparation, voltage switch, timeout programming, DRTO calculation, and hardware reset.
- `mci_readl()` and `mci_writel()` wrap relaxed access to named `SDMMC_*` registers.
- `mci_fifo_readw/l/q()` and `mci_fifo_writew/l/q()` provide raw FIFO access. `mci_fifo_l_readq()` and `mci_fifo_l_writeq()` emulate 64-bit FIFO access as two 32-bit accesses for controllers with `DW_MMC_QUIRK_FIFO64_32`.
- External core functions are declared: `dw_mci_alloc_host`, `dw_mci_probe`, `dw_mci_remove`, `dw_mci_runtime_suspend`, and `dw_mci_runtime_resume`.

## Control Flow And State

The header documents the state model expected by implementation files. Interrupt handlers snapshot controller status into `cmd_status` and `data_status`, set bits in `pending_events`, and the `bh_work` worker advances `state` while updating `completed_events`. Active request pointers (`mrq`, `cmd`, `data`) and state are guarded by `host->lock`; interrupt-mask updates are isolated under `irq_lock`. The comments emphasize ordering before setting event bits: data interrupts must be disabled and status captured before `EVENT_DATA_*`, command-ready interrupt must be disabled and status captured before `EVENT_CMD_COMPLETE`, and bytes transferred must be committed before `EVENT_XFER_COMPLETE`.

DMA state is persistent across a request via `use_dma`, `using_dma`, descriptor ring fields, external DMA slave data, and request cookies. FIFO PIO state persists across partial transfers using `sg`, `sg_miter`, `part_buf_start`, `part_buf_count`, and `part_buf`.

## Dependencies And Integration Points

The header depends on Linux MMC core types, DMAEngine, reset control, fault injection, hrtimers, IRQs, scatterlists, workqueues, and platform driver infrastructure. It integrates DesignWare core logic with SoC-specific wrappers through `dw_mci_drv_data`, with DMA engines through `dw_mci_dma_ops`, with the MMC host core through `struct mmc_host`, and with runtime PM through exported suspend/resume declarations.

Register definitions span the base controller, IDMAC 32-bit and 64-bit descriptor layouts, UHS/DDR/HS400 controls, clock, timeout, interrupt, FIFO threshold, and command formatting fields. Platform code is expected to use these definitions instead of open-coded offsets.

## Risks And Edge Cases

- Locking/order violations around `pending_events`, status snapshots, and interrupt masking can produce lost completions or double completion.
- FIFO endian and width handling is sensitive; the 64-bit FIFO-as-two-32-bit helper exists for controllers that cannot safely use raw 64-bit operations.
- `mci_fifo_writew()`/`mci_fifo_writel()` macro argument order is unusual because the raw write macros take value then register; callers must use the wrapper as defined.
- Timer fields for CMD11, command timeout, and data timeout imply recovery paths outside this header; variant code must coordinate with them.
- `struct dw_mci_drv_data` callbacks are optional, so core code must null-check and provide defaults.

## Test Signals

Useful validation signals include boot/probe of multiple DesignWare variants, PIO and IDMAC/EDMAC transfers, pre_req/post_req DMA mapping reuse, SDIO IRQ delivery, voltage switch CMD11, tuning/HS400 paths, FIFO64_32 quirk coverage on 64-bit kernels, runtime suspend/resume, and fault-injection induced data CRC failures when configured.
