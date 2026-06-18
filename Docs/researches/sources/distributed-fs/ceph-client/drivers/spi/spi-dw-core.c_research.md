# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-core.c

## Purpose

`spi-dw-core.c` is the shared Synopsys DesignWare SPI controller core used by glue drivers. It provides controller registration/removal, FIFO-based PIO and IRQ transfers, optional DMA integration, target-mode abort, debugfs registers, native chip-select control, `spi-mem` execution for standard native-CS APB SSI controllers, and suspend/resume helpers.

## Important APIs, Types, and Functions

Externally visible APIs include `dw_spi_add_controller()`, `dw_spi_remove_controller()`, `dw_spi_suspend_controller()`, `dw_spi_resume_controller()`, `dw_spi_set_cs()`, `dw_spi_update_config()`, and `dw_spi_check_status()`. Runtime helpers include `dw_writer()`, `dw_reader()`, `dw_spi_transfer_handler()`, `dw_spi_irq()`, `dw_spi_prepare_cr0()`, `dw_spi_irq_setup()`, `dw_spi_poll_transfer()`, `dw_spi_transfer_one()`, `dw_spi_abort()`, and `dw_spi_hw_init()`.

The `spi-mem` path is implemented by `dw_spi_adjust_mem_op_size()`, `dw_spi_supports_mem_op()`, `dw_spi_init_mem_buf()`, `dw_spi_write_then_read()`, `dw_spi_wait_mem_op_done()`, `dw_spi_stop_mem_op()`, `dw_spi_exec_mem_op()`, and `dw_spi_init_mem_ops()`. Per-device state is `struct dw_spi_chip_data`, storing prepared CR0 and RX sample delay.

## Control Flow

Glue drivers fill `struct dw_spi` and call `dw_spi_add_controller()`. The core allocates host or target controller based on `spi-slave`, initializes hardware, requests IRQ unless disconnected, installs default mem ops when appropriate, configures controller capabilities, initializes DMA if supplied, registers the controller, and creates debugfs.

Normal transfers disable the chip, update CTRLR0/CTRLR1/clock/sample delay, detect DMA mapping, mask interrupts, set up DMA if needed, enable the chip, then execute via DMA, poll mode, or IRQ mode. IRQ mode uses TX/RX FIFO thresholds and finalizes when RX length reaches zero. Poll mode repeatedly writes as much as possible, delays for expected receive clocks, reads FIFO, and checks raw status. Error handling aborts DMA if active and resets the chip.

The default `spi-mem` implementation packs opcode/address/dummy/TX data into one buffer, programs transmit-only or EEPROM-read mode, enables the controller, disables local interrupts and preemption, manually keeps TX FIFO nonempty while native CS is active, drains RX fast enough to avoid overflow, waits for busy to clear, checks errors, deasserts CS, and frees temporary buffers.

## State and Persistence Behavior

The core maintains controller state in `struct dw_spi`: FIFO length, number of chip selects, version/capabilities, max/current frequency, DMA state, current transfer buffers and counts, debugfs, and per-controller memory buffer. Per-SPI-device `dw_spi_chip_data` persists from setup to cleanup. There is no file-backed persistence; hardware register state is reset during init, remove, suspend, and error abort.

## Dependencies and Integration Points

The core depends on glue-provided `struct dw_spi` fields from `spi-dw.h`, SPI controller APIs, optional DMA ops, interrupts, MMIO accessors, debugfs, firmware properties, `spi-mem`, preemption/IRQ control, and namespace exports `SPI_DW_CORE`. It supports PSSI and HSSI register-layout differences and optional capabilities such as `DW_SPI_CAP_DFS32` and `DW_SPI_CAP_CS_OVERRIDE`.

## Risks and Edge Cases

The `spi-mem` path intentionally disables local IRQs/preemption and can still fail on slow buses/CPUs if the FIFO drains or RX overflows; platform glue must cap `max_mem_freq` appropriately. `free_irq(dws->irq, ...)` is called even when `request_irq()` returned `-ENOTCONN`, so disconnected IRQ configurations should be checked. FIFO and CS autodetection write test values to hardware registers and assume reversible side effects. Per-device setup allocates state and must be paired with cleanup. DMA setup failures occur after chip configuration and before chip enable, so glue DMA ops must leave consistent state.

## Test Signals

Tests should cover glue-driver add/remove with connected and disconnected IRQs, host and target mode, FIFO/CS/DFS autodetection, PSSI and HSSI CR0 fields, 4- through 32-bit transfers, IRQ, poll, and DMA paths, RX/TX overflow/underflow handling, target abort, suspend/resume, debugfs register exposure, default `spi-mem` reads/writes with native CS, GPIO CS fallback, `rx-sample-delay-ns` properties, and low `max_mem_freq` mitigation of CS underrun.
