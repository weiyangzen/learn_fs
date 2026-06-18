# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hwio.c

Purpose: Implements low-level WFx register, data-queue, SRAM, and AHB I/O using the selected bus operations.

Important APIs and functions: Public helpers include `wfx_data_read()`, `wfx_data_write()`, SRAM/AHB buffer and register read/write, config/control register read/write/write_bits, and IGPR read/write. Internal helpers perform 32-bit register I/O, masked read-modify-write, indirect SRAM/AHB access through base address and prefetch bits, and locked tracing variants.

Control flow and integration: Firmware boot uses SRAM/AHB access for DCA/FIFO/GPR/register setup. BH uses data queue and control/config register access. Common probe and shutdown use config/control operations. All public helpers lock/unlock through `hwbus_ops`, perform endian conversion for 32-bit values, and trace accesses.

State and persistence: The code does not own driver state beyond transient buffers, but it mutates chip config/control/base/IGPR/SRAM/AHB registers and relies on bus-level serialization.

Dependencies: Depends on `wfx_hwbus_ops`, bus register IDs, chip config/control bit definitions, tracepoints, kmalloc-backed DMA-safe temporary buffers, and firmware register semantics.

Risks and test signals: Risks include stack/vmalloc buffers passed to DMA-capable bus ops, unaligned buffers, indirect prefetch timeout, masked writes with invalid values, lock/unlock imbalance, returning undefined values after failed reads, and register endian errors. Tests should cover config/control reads/writes, write_bits, data queue alignment, SRAM/AHB buffer and register access, prefetch timeout path, IGPR access, and injected bus errors on SPI/SDIO.

Test signals: Source read size: 332 lines, 8438 bytes.
