<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c

## Purpose
`xilinx-spi.c` is a slave-serial SPI transport for Xilinx Spartan-6 and 7 Series FPGA configuration. It supplies chunked SPI writes to the shared Xilinx FPGA manager core.

## Important APIs, types, and functions
`xilinx_spi_write()` implements the `xilinx_fpga_core.write` callback and sends firmware data with `spi_write()` in chunks of at most `SZ_4K`. `xilinx_spi_probe()` allocates `struct xilinx_fpga_core`, stores the SPI device as `core->dev`, and calls `xilinx_core_probe()`.

## Control flow
When the SPI driver probes a matching device, it registers through the common Xilinx core. During programming, the core handles GPIO sequencing and calls `xilinx_spi_write()`, which advances through the firmware buffer in 4 KiB strides and aborts on the first SPI transfer error.

## State and persistence behavior
The only private state is the devm-allocated `struct xilinx_fpga_core`. SPI controller/device state and FPGA programming state are external; no persistent state is stored.

## Dependencies and integration points
It depends on SPI core, OF/SPI IDs (`fpga-slave-serial`, `xlnx,fpga-slave-serial`), module SPI driver registration, and `xilinx-core`. The common core handles manager registration and GPIOs.

## Risks and edge cases
Large firmware images are serialized synchronously and depend on SPI controller behavior for chip select and clocking. Errors after partial writes cannot be recovered locally. The driver delegates partial-reconfiguration rejection and completion polling to `xilinx-core`.

## Test signals
SPI probe, successful manager registration, firmware writes larger and smaller than 4 KiB, SPI error propagation, and common-core completion behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-spi.c -->
