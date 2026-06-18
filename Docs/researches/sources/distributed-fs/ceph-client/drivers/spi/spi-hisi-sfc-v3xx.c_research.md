# sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-sfc-v3xx.c

## Purpose

`spi-hisi-sfc-v3xx.c` is a HiSilicon V3XX SPI NOR flash controller driver for hi16xx-class chipsets. It exposes a `spi_mem` controller that executes command/address/dummy/data flash operations through controller command registers and a small DATABUF window, using either IRQ completion or polling.

## Important APIs, Types, and Functions

`struct hisi_sfc_v3xx_host` stores device, MMIO base, max command dwords, optional IRQ/completion, and fixed address mode. `hisi_sfc_v3xx_mem_ops` provides `adjust_op_size`, `supports_op`, and `exec_op`. Data buffer helpers `hisi_sfc_v3xx_read_databuf()` and `hisi_sfc_v3xx_write_databuf()` enforce 32-bit MMIO accesses with byte handling for tails and unaligned host buffers. `hisi_sfc_v3xx_start_bus()` composes command config, bus width mode, dummy count, chip select, direction, and start bit. `hisi_sfc_v3xx_handle_completion()` decodes completion, protected-address, and page-program errors.

## Control Flow

Module init first applies DMI quirks that force quad buswidth override on selected Huawei systems. Probe allocates a host, maps MMIO, optionally requests IRQ, disables interrupts, configures a single-chipselect spi-mem controller, reads global configuration to determine 3-byte versus 4-byte address mode, selects command-buffer size from hardware version, and registers the controller.

For each spi-mem op, `supports_op()` rejects bus widths above quad and address lengths that do not match the controller's read-only address mode. `adjust_op_size()` limits data to the DATABUF size and, for unaligned buffers with at least four bytes, trims the operation to reach alignment. `exec_op()` optionally enables interrupts and stores an on-stack completion, writes outgoing data, starts the bus command, waits by IRQ or by polling the start bit clear, decodes raw interrupt status, and reads incoming data.

## State and Persistence Behavior

The host structure persists only controller configuration: IRQ availability, command-buffer size, and address mode. `host->completion` is transient during one IRQ-backed operation. Flash contents are the only persistent state affected by write/program/erase commands. Interrupt masks are enabled only during a command and disabled afterward.

## Dependencies and Integration Points

The driver integrates with ACPI id `HISI0341`, DMI board quirks, platform MMIO/IRQ resources, and the SPI memory layer used by SPI NOR. It relies on `spi_mem_default_supports_op()` after its own buswidth/address checks. It uses raw 32-bit IO copy helpers because the hardware data registers require 32-bit accesses.

## Risks and Edge Cases

IRQ mode uses an on-stack completion pointer in the host; it disables interrupts, synchronizes the IRQ, and clears the pointer after each command, so tests should stress timeout/IRQ races. `hisi_sfc_v3xx_generic_exec_op()` collapses either wait failure or completion-status failure to `-EIO`, losing `-ETIMEDOUT` detail. Dummy count and data count are programmed directly from op fields and must fit hardware bitfields. Address mode is global and read-only, so devices needing mixed 3-byte/4-byte operations are not supported unless the controller is configured accordingly.

## Test Signals

Test IRQ and polling operation, hardware versions below/above `0x351`, 3-byte and 4-byte address modes, DMI quad override systems, unaligned read/write buffers, operations at 16-dword and 64-dword limits, unsupported buswidth matrices, protected address errors, page program errors, completion timeouts, and SPI NOR probe/read/program/erase paths.
