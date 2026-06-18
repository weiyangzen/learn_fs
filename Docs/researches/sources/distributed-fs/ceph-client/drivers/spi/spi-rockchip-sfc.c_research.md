# sources/distributed-fs/ceph-client/drivers/spi/spi-rockchip-sfc.c

## Purpose

`spi-rockchip-sfc.c` is a Linux `spi-mem` controller driver for the Rockchip Serial Flash Controller. It is specialized for SPI NOR/NAND-style memory transactions rather than generic full-duplex SPI. The driver programs SFC command, address, dummy, data-width, length, chip-select, FIFO, DMA, interrupt, clock, and runtime-PM registers and exposes the controller through `struct spi_controller_mem_ops`.

## Important APIs, Types, and Functions

`struct rockchip_sfc` stores MMIO base, bus/interface clocks, per-chip-select cached speeds, a coherent-ish DMA bounce buffer, a DMA completion, controller version, maximum I/O size, and the registered SPI host. Register helpers include `rockchip_sfc_reset()`, `rockchip_sfc_get_version()`, `rockchip_sfc_clk_set_rate()`, `rockchip_sfc_irq_mask()`, and `rockchip_sfc_init()`.

The transfer path is split into `rockchip_sfc_adjust_op_work()`, `rockchip_sfc_xfer_setup()`, FIFO helpers `rockchip_sfc_write_fifo()` and `rockchip_sfc_read_fifo()`, DMA helpers `rockchip_sfc_fifo_transfer_dma()` and `rockchip_sfc_xfer_data_dma()`, and completion wait `rockchip_sfc_xfer_done()`. The exported memory hooks are `rockchip_sfc_exec_mem_op()` and `rockchip_sfc_adjust_op_size()` in `rockchip_sfc_mem_ops`. Probe/remove and PM are handled by `rockchip_sfc_probe()`, `rockchip_sfc_remove()`, runtime suspend/resume, and system suspend/resume.

## Control Flow

Probe allocates a SPI host, maps registers, gets clocks or ACPI `clock-frequency`, decides whether DMA is enabled from `rockchip,sfc-no-dma`, enables clocks, requests the IRQ, initializes the controller, records hardware version and max I/O size, enables runtime PM, optionally allocates and maps a DMA bounce buffer, then registers the controller. `exec_op` takes a runtime-PM reference, adjusts the interface clock when `per_op_freq` changes, rewrites dummy-without-address operations into address cycles, programs command/address/dummy/data registers, transfers data via DMA for aligned large buffers or PIO FIFO loops otherwise, waits for the controller to go idle, and drops the PM reference.

DMA transfer starts by unmasking the DMA interrupt, writing the bounce-buffer DMA address, and triggering the SFC DMA engine. The IRQ handler clears raw interrupt status and completes `sfc->cp` on `SFC_RISR_DMA`. PIO transfer polls FIFO fill levels before each repeated MMIO read/write. Resume reinitializes the controller after clocks and pinctrl state are restored.

## State and Persistence Behavior

The driver has no file-backed persistence. Runtime state is the controller register image, per-CS speed cache, runtime-PM clock state, DMA buffer mapping, and transfer completion. Persistent external effects are flash-memory operations initiated by upper-layer spi-mem clients; this file only transports those operations.

`rockchip_sfc_adjust_op_size()` clamps each operation to `max_iosize`. Versions 4+ use `SFC_LEN_EXT` and `SFC_LEN_CTRL_TRB_SEL`; older versions encode length in `SFC_CMD`. Version 8 doubles the configured source clock relative to the observed SFC bus rate.

## Dependencies and Integration Points

The driver integrates with Linux platform devices, OF/ACPI properties, clocks, runtime PM, pinctrl sleep/default states, interrupts, DMA mapping, and the `spi-mem` framework. It supports dual/quad TX/RX mode bits, two native chip selects, half-duplex transfers, and per-operation frequency selection. Flash protocol semantics are supplied by spi-mem consumers.

## Risks and Edge Cases

`rockchip_sfc_get_max_iosize()` always returns the version-3 limit even though version-4 constants exist; if newer hardware can safely transfer larger chunks this underuses it, while if version-specific limits differ in the other direction it could be wrong. DMA uses a single bounce buffer allocated with `GFP_DMA32` and writes only the low 32 bits of the DMA address, so the mapping must be 32-bit-addressable. `rockchip_sfc_exec_mem_op()` casts away `const` to adjust the op, which relies on spi-mem callers tolerating mutation. Removal unmaps/frees the DMA buffer unconditionally; this is benign only if the fields are zero/NULL when DMA was disabled. Error paths must keep runtime-PM and clock state balanced after partial probe failures.

## Test Signals

Useful tests include spi-nor probe/read/write/erase on both chip selects, odd-length PIO transfers, aligned and unaligned large reads/writes crossing the DMA threshold, dummy-cycle-only operations, 3-byte and 4-byte addressing, per-op frequency switching, DMA timeout injection, FIFO timeout injection, runtime suspend/resume during idle, and system suspend/resume followed by flash reads.
