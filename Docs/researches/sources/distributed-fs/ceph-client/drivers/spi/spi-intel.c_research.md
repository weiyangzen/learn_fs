# sources/distributed-fs/ceph-client/drivers/spi/spi-intel.c

## Purpose

`spi-intel.c` is the shared Intel PCH/PCU SPI flash controller core. It exposes the controller as a `spi_mem` host for SPI NOR, supports hardware and software sequencer operations, enforces or reports flash protection state, reads the Intel flash descriptor to size components and partitions, creates SPI NOR child devices, and exports sysfs status attributes for protected, locked, and BIOS-locked state.

## Important APIs, Types, and Functions

`struct intel_spi` holds device, boardinfo, MMIO bases, protection/software-sequencer register offsets, host pointer, region/protection counts, flash chip size, lock/protection flags, software-sequencer flags, atomic preopcode state, BIOS-programmed opcodes, and selected memory-operation table. `struct intel_spi_mem_op` maps a `spi_mem_op` shape to an execution helper and optional hardware replacement cycle.

Core execution helpers include `intel_spi_hw_cycle()`, `intel_spi_sw_cycle()`, `intel_spi_read_reg()`, `intel_spi_write_reg()`, `intel_spi_read()`, `intel_spi_write()`, and `intel_spi_erase()`. spi-mem callbacks are `intel_spi_adjust_op_size()`, `intel_spi_supports_mem_op()`, `intel_spi_exec_mem_op()`, direct-map create/read/write, and `intel_spi_get_name()`. Initialization and discovery are handled by `intel_spi_init()`, `intel_spi_read_desc()`, `intel_spi_fill_partition()`, `intel_spi_populate_chip()`, and exported `intel_spi_probe()`.

## Control Flow

`intel_spi_probe()` allocates a SPI host, stores MMIO and boardinfo, runs `intel_spi_init()`, registers the controller, stores driver data, and populates SPI NOR child devices. Init selects register offsets and capabilities by boardinfo type, optionally asks the front-end to disable BIOS write protection when `writeable=1`, disables sequencer SMI generation, decides whether erase must use software sequencing based on LVSCC/UVSCC opcodes, verifies software sequencer availability, reads lock state and BIOS opmenu opcodes, chooses generic or 64K-erase operation tables, and dumps debug registers.

spi-mem support matches incoming ops against static operation tables. Register ops use hardware replacement cycles when possible or software sequencer cycles for programmable opcodes. Write-enable is represented as an atomic preopcode for the following software-sequencer write. Bulk reads/writes use the hardware sequencer in chunks no larger than the 64-byte FIFO and not crossing 4 KiB boundaries. Erase uses hardware or software sequencing depending on init decisions. Direct-map operations reuse the matched operation helper.

Flash population reads descriptor signature and component-density data, sets one or two chip selects, creates a `spi-nor` board info for chip 0 with a `BIOS` partition covering enabled regions, marks it read-only if writeable was not requested or protected regions exist, and optionally creates chip 1 with a full-size `BIOS1` partition.

## State and Persistence Behavior

Driver state persists in `struct intel_spi` for the controller lifetime. `protected`, `locked`, and `bios_locked` are exposed read-only through sysfs. The module parameters `writeable` and `ignore_protection_status` affect whether the MTD partition is writeable and whether protected-region status blocks writes. Flash writes/erases persist in SPI NOR storage; BIOS control register changes can alter platform flash writeability. The driver itself stores no file-backed state.

## Dependencies and Integration Points

The core depends on SPI memory APIs, SPI NOR opcodes, MTD partition data, Intel boardinfo from x86 platform data, MMIO accessors, polling helpers, and the PCI/platform wrappers. It exports `intel_spi_probe()` and `intel_spi_groups` for those wrappers. It integrates with SPI NOR by creating `spi-nor` devices programmatically instead of relying on firmware child nodes.

## Risks and Edge Cases

This is security-sensitive firmware flash access. The `writeable` and `ignore_protection_status` parameters can expose BIOS regions for modification. Software sequencer support depends on BIOS-programmed locked opmenus; unsupported opcodes must be rejected. `intel_spi_is_protected()` returns true only when a protected range is contained within a flash region, so range-overlap semantics deserve review. Hardware cycles must not cross 4 KiB boundaries, and FIFO chunks are limited to 64 bytes. Descriptor parsing failure prevents child creation. Atomic preopcode state must be cleared after each relevant operation to avoid applying WREN to the wrong command.

## Test Signals

Test BYT/LPT/BXT/CNL boardinfo paths, locked and unlocked opmenus, hardware versus software sequencer register access, 4K and 64K erase selection, descriptor read failures, one-chip and two-chip descriptors, protected range sysfs, BIOS lock sysfs, `writeable` and `ignore_protection_status` combinations, 64-byte FIFO chunking, 4 KiB boundary splitting, WREN atomic sequence behavior, direct-map reads/writes, and SPI NOR probe/read/program/erase flows.
