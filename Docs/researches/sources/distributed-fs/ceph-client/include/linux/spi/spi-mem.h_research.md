<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h

Purpose: This header defines the SPI memory abstraction used by flash-like devices and QSPI/OSPI controllers, expressing operations as command/address/dummy/data phases rather than generic byte transfers.

Important APIs/types/functions: Builder macros create STR/DTR command, address, dummy, data, and full `SPI_MEM_OP()` descriptors. `spi_mem_op` carries phase widths, DTR, ECC, swap16, direction, byte counts, buffers, and per-operation max frequency. Direct mapping types are `spi_mem_dirmap_info` and `spi_mem_dirmap_desc`. `spi_mem` wraps a `spi_device`; `spi_controller_mem_ops` supplies adjust/support/exec/name/dirmap/poll callbacks; `spi_controller_mem_caps` advertises DTR/ECC/swap16/per-op frequency. `spi_mem_driver` wraps `spi_driver`.

Control flow: Memory drivers build an operation, adjust size/frequency, check support, then execute it or use direct mapping. Direct mapping creation may fall back to `exec_op()` through `nodirmap`, letting drivers use one path even when hardware lacks mapping support.

State and persistence: `spi_mem` stores driver private data and name; dirmap descriptors persist mapping metadata and provider private state until destroyed. Hardware memory contents persist externally.

Dependencies/integration: Depends on SPI core, DMA scatterlists for mapped data, SPI NOR/NAND-style drivers, and QSPI controller native mem ops. Disabled `CONFIG_SPI_MEM` stubs return unsupported/default false for DMA/support helpers.

Risks and test signals: Risks include duplicate macro definition for `SPI_MEM_DTR_OP_RPT_ADDR`, bad address-width/value fit, DTR phase mismatches, direct-map short I/O handling, unsupported ECC/swap16 use, and DMA mapping lifetime. Test with JEDEC read, page program, erase/status polling, DTR octal modes, direct-map fallback and partial reads/writes, and controller capability negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi-mem.h -->
