<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c

## Purpose

`spi-wpcm-fiu.c` is a SPI memory controller driver for the Nuvoton WPCM450 Flash Interface Unit. It implements `spi-mem` operations over the FIU's User Mode Access (UMA) registers and supports direct mapped flash reads through the FIU memory window.

The hardware can handle only small UMA data payloads and has special behavior for some flash commands, so the driver classifies operations into supported shapes and executes multi-step sequences where needed.

## Important APIs, Types, and Functions

`struct wpcm_fiu_spi` stores device, clock, control register mapping, direct memory window mapping/size, and optional SHM syscon regmap used to stall host flash accesses during UMA transfers.

Low-level UMA helpers are `wpcm_fiu_set_opcode()`, `wpcm_fiu_set_addr()`, `wpcm_fiu_set_data()`, `wpcm_fiu_get_data()`, `wpcm_fiu_do_uma()`, `wpcm_fiu_ects_assert()`, and `wpcm_fiu_ects_deassert()`.

`struct wpcm_fiu_op_shape` binds a matcher to an executor. Supported shapes are normal command/address/no-dummy operations with up to 4 data bytes, a fast-read matcher that currently returns `-EINVAL`, 4-byte-address operations split into two UMA cycles, RDID six-byte reads split into two reads, and operations with dummy bytes split across asserted chip select.

SPI memory callbacks are `wpcm_fiu_supports_op()`, `wpcm_fiu_exec_op()`, `wpcm_fiu_adjust_op_size()`, `wpcm_fiu_dirmap_create()`, and `wpcm_fiu_direct_read()`. `wpcm_fiu_hw_init()` configures the flash memory window and deasserts manual chip selects. `wpcm_fiu_probe()` maps resources, enables the clock, initializes hardware, fills `mem_ops`, and registers the controller.

## Control Flow

Probe allocates a SPI host, maps `"control"` registers and `"memory"` flash window, enables the FIU clock, optionally resolves a `"nuvoton,shm"` syscon, initializes burst/window registers, sets all manual chip selects deasserted, and registers a four-chip-select SPI memory controller. The controller min and max speeds are both the AHB3 clock because the FIU has no divider.

Before executing a SPI memory operation, `supports_op` first asks the SPI MEM core for default support, rejects DTR and multi-bit bus widths, then finds a matching shape. `adjust_op_size` clamps data payloads to 4 bytes because UMA has four data registers.

`exec_op` stalls host flash-memory accesses through SHM when available, finds the shape, and executes it. Normal operations write opcode/address/data registers, run one UMA command with address/write/data-size flags, and read data registers on input. Four-byte addressing asserts manual chip select and emits the high three address bytes as one UMA phase, then uses the low address byte as a pseudo opcode for the second phase. RDID performs two reads because FIU can read only up to four bytes. Dummy-byte operations assert chip select, send opcode/address plus dummy bytes as a write-like phase, then run a read phase.

Direct mapping validates that the operation is read-only, the requested mapping does not cross the 16 MiB per-chip window, and the requested chip-select window exists in the mapped memory resource. Direct reads copy from the appropriate `cs * 16 MiB + offset` MMIO memory window.

## State and Persistence Behavior

The driver keeps only volatile controller mappings and optional SHM regmap state. It writes FIU configuration registers during probe and UMA control/data registers per operation. SPI flash contents can be changed by write/erase commands issued through UMA, but the driver itself stores no persistent metadata.

Manual chip-select state is controlled by the ECTS register during multi-phase operations. Host memory access stalling is intended to be temporary around UMA transfers so the BMC host side does not collide with software-controlled accesses.

## Dependencies and Integration Points

The driver depends on platform resources named `"control"` and `"memory"`, device tree compatible `"nuvoton,wpcm450-fiu"`, clocks, MMIO byte accessors, regmap/syscon, and the SPI MEM framework.

It integrates with SPI NOR or other SPI memory clients through `spi_controller_mem_ops`, including both `exec_op` and direct-map reads. The optional SHM syscon integration updates `SHM_FLASH_SIZE_STALL_HOST`.

## Risks and Edge Cases

`wpcm_fiu_exec_op()` stalls host access before executing a matching shape but returns directly from `shape->exec()` without unstalling the host. The unstall path is only reached when no shape is found. That is a strong bug signal unless some external mechanism clears the stall bit.

Several shape executors ignore return values from `wpcm_fiu_do_uma()`, especially multi-phase 4-byte address, RDID, and dummy paths. A timed-out UMA phase can still produce success and stale data.

`wpcm_fiu_fast_read_match()` accepts opcode `0x0b`, but its executor always returns `-EINVAL`; because `supports_op()` only checks for a shape, the core may choose an operation that later fails. This is a mismatch between capability advertisement and execution.

The operation-shape model only supports single-bit bus widths, no DTR, small payloads, and limited dummy handling. The direct-map path cannot represent partial mappings larger than the per-chip 16 MiB window.

## Test Signals

Tests should exercise normal opcode-only, address-only, read, write, 4-byte address, six-byte RDID, dummy-byte reads, unsupported fast read, unsupported DTR and multi-bit bus widths, and `adjust_op_size` truncation.

Fault tests should verify UMA timeout propagation, host stall/un-stall behavior, absent SHM regmap, direct-map bounds per chip select, memory resource smaller than advertised, and write/erase command behavior through SPI NOR clients. Static analysis should flag the missing unstall after successful `exec_op` and ignored UMA return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c -->
