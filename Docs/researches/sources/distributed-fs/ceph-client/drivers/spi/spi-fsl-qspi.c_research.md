# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-qspi.c

## Purpose
Implements a Freescale/NXP QuadSPI controller using the SPI MEM API. It programs a single reusable LUT entry per operation, supports per-operation clock frequency, uses IP commands for small operations, uses AHB memory mapping for larger reads, and handles multiple SoC-specific quirks.

## Important APIs, Types, And Functions
`struct fsl_qspi_devtype_data` captures FIFO sizes, AHB buffer size, invalid master ID, address-window size, quirks, and register endianness. `struct fsl_qspi` stores MMIO/AHB mappings, clocks, reset, lock, completion, PM QoS request, selected CS, and memory-map base. SPI MEM callbacks are `fsl_qspi_adjust_op_size()`, `fsl_qspi_supports_op()`, `fsl_qspi_exec_op()`, and `fsl_qspi_get_name()`. Other key functions include `fsl_qspi_prepare_lut()`, `fsl_qspi_select_mem()`, `fsl_qspi_fill_txfifo()`, `fsl_qspi_read_rxfifo()`, `fsl_qspi_do_op()`, `fsl_qspi_default_setup()`, and probe/cleanup helpers.

## Control Flow
Probe allocates a SPI host, maps controller and AHB memory resources, obtains reset and clocks, enables clocks, deasserts reset, requests IRQ, sets four chip selects, installs SPI MEM ops/caps, performs default hardware setup, and registers the controller. `exec_op()` serializes with a mutex, waits for IP/AHB idle, selects chip and rate, programs SFAR, clears FIFOs/pointers, invalidates AHB buffer ownership, programs the LUT for command/address/dummy/data, then either copies large reads from AHB mapping or fills TX FIFO and launches an IP command. The IRQ completes transfer-finished events.

## State And Persistence
The selected chip index, LUT contents, clock rate, AHB buffer configuration, and reset state are runtime hardware/software state. The driver invalidates AHB buffers after operations to avoid stale reads. No persistent storage is used.

## Dependencies And Integration Points
Depends on SPI MEM, clk, reset, platform named resources `QuadSPI` and `QuadSPI-memory`, IRQ completion, mutex locking, PM QoS for wait-mode erratum, and OF compatible data for Vybrid, i.MX6/7, Layerscape, and Spacemit K1 variants.

## Risks
LUT construction is limited to operations fitting a single LUT entry and dummy cycles <=64. Read sizes have alignment constraints around RX FIFO vs AHB path. Quirk handling controls endian swapping, 4x clocks, minimum TX FIFO fill, AMBA base offsets, TDH clearing, and clock-disable behavior; wrong variant data can corrupt operations. `fsl_qspi_select_mem()` returns void, so clock-rate failures are not propagated to `exec_op()`.

## Test Signals
SPI NOR probe/read/write/erase across bus widths, large AHB reads, unaligned near-FIFO-size reads, TX FIFO fill erratum, endian variants, per-op frequency switching, suspend/resume default setup, timeout on missing IRQ, and multi-CS naming/selection should be tested.
