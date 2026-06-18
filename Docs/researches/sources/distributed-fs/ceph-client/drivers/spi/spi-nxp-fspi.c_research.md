<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c

## Purpose

`spi-nxp-fspi.c` is the NXP FlexSPI controller driver. It exposes a SPI-MEM-only controller for NOR-like memories connected through single, dual, quad, or octal lines. FlexSPI executes operations through runtime-generated LUT sequences, uses IP bus FIFO access for small operations, uses AHB memory mapping for larger reads when safe, supports selected DTR operation, and handles SoC quirks and endianness differences.

## Important APIs, Types, and Functions

`struct nxp_fspi_devtype_data` describes FIFO sizes, AHB buffer size, quirks, LUT count, and register endianness. `struct nxp_fspi` stores controller registers, AHB mapping, physical memory window, clocks, device, completion, devtype data, mutex, selected chip state, flags, prior operation rate, and max output rate.

Register access is wrapped by `fspi_writel()` and `fspi_readl()` for big/little-endian controllers. SPI-MEM callbacks are `nxp_fspi_supports_op()`, `nxp_fspi_adjust_op_size()`, `nxp_fspi_exec_op()`, and `nxp_fspi_get_name()`. Execution helpers include `nxp_fspi_select_mem()`, `nxp_fspi_prepare_lut()`, `nxp_fspi_fill_txfifo()`, `nxp_fspi_read_rxfifo()`, `nxp_fspi_do_op()`, `nxp_fspi_read_ahb()`, and `nxp_fspi_invalid()`. Setup and PM helpers include `nxp_fspi_default_setup()`, `nxp_fspi_select_rx_sample_clk_source()`, `nxp_fspi_dll_calibration()`, `nxp_fspi_dll_override()`, runtime suspend/resume, and system suspend.

## Control Flow

Probe allocates the controller, loads devtype data, maps register and memory resources, obtains clocks for OF systems, enables runtime PM, powers the device, clears stale interrupts, runs default setup, powers down, requests IRQ, initializes a mutex, assigns SPI-MEM ops/caps, registers cleanup, and registers the controller. ACPI systems skip Linux clock operations.

`supports_op` validates bus widths, address size, address range within the memory-mapped aperture, dummy cycles, and FIFO/AHB size/alignment constraints. `adjust_op_size` constrains writes to TX FIFO size, reads to AHB buffer size, aligns reads that exceed RX FIFO minus four bytes, and further limits reads on IP-only quirked SoCs.

`exec_op` serializes with a mutex, resumes runtime PM, waits for arbitration idle, selects the target chip and clock mode, writes a LUT sequence for command/address/dummy/data, and chooses AHB or IP execution. Larger reads use `ioremap` of the AHB flash window and `memcpy_fromio()` unless an IP-only quirk is set. Writes preload TX FIFO. IP execution programs IPCR address, sequence id, and data size, triggers the command, waits for interrupt completion, and reads RX FIFO for read operations. Every operation invalidates AHB buffers by software-resetting the controller before autosuspend.

## State and Persistence Behavior

`selected`, `FSPI_DTR_MODE`, and `pre_op_rate` cache chip-select and clock/DTR configuration to avoid redundant reprogramming. `ahb_addr`, `memmap_start`, and `memmap_len` cache the currently mapped AHB window and are replaced when a read falls outside it. `FSPI_NEED_INIT` forces full hardware setup after system suspend.

The driver has no file persistence. Flash contents are changed only through upper-layer SPI-MEM program/erase commands.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, platform/OF/ACPI matching, runtime/system PM, pinctrl PM, clocks, interrupts, completions, mutexes, IO remapping, syscon/regmap for LS1028A erratum detection, SoC matching, and device-tree memory resources `fspi_base` and `fspi_mmap`.

## Risks and Edge Cases

The driver uses the last LUT slot dynamically for every operation; concurrent execution is protected by a mutex and must remain so. AHB reads are invalidated after all operations, but write/erase data coherency still depends on correct reset timing. DTR support is limited to full 8D-8D-8D style operation, and some devtypes disable DTR entirely. Clock switching disables clocks, changes rate, re-enables clocks, and recalibrates DLL above 100 MHz; failures can leave previous selections stale.

`nxp_fspi_cleanup()` calls `pm_runtime_get_sync()` but does not check failure before register access. Probe error paths after runtime PM enable need careful coverage.

## Test Signals

Tests should cover each devtype, little- and big-endian register access where applicable, command/address/dummy/data LUT generation, single/dual/quad/octal widths, DTR enable/disable caps, IP reads and writes at FIFO limits, AHB reads and ioremap window reuse/replacement, IP-only quirk behavior, LS1028A erratum detection, clock-rate switching and DLL paths above/below 100 MHz, runtime autosuspend, system suspend with reinit, IRQ timeout, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-nxp-fspi.c -->
