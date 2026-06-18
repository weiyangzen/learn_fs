<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h

Purpose: This header defines platform data for Xilinx SPI controller drivers.

Important APIs/types/functions: `xspi_platform_data` supplies child `spi_board_info` entries, child count, chip-select count, bits-per-word value, and `force_irq` for QSPI transaction requirements.

Control flow: Controller probe uses this data to register child devices, set chip-select capacity, configure word width, and choose interrupt-forced behavior when required.

State and persistence: Static platform data only. Controller runtime state is driver-owned.

Dependencies/integration: Depends on kernel types and forward-declared `spi_board_info`; integrates with Xilinx SPI/QSPI controller and board files.

Risks and test signals: Risks include registering wrong child devices, unsupported bits-per-word, insufficient chip-select count, and forced IRQ path regressions. Test child enumeration, word-size transfers, IRQ/PIO behavior, and multi-device buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/xilinx_spi.h -->
