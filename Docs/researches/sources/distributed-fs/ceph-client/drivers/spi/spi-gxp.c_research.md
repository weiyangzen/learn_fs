# sources/distributed-fs/ceph-client/drivers/spi/spi-gxp.c

## Purpose

`spi-gxp.c` is the HPE GXP SPI flash interface driver. It registers a SPI host with `spi_mem` operations and uses the GXP SPIFI controller in manual/direct modes to perform SPI NOR register, read, and page-program style operations against up to two chip selects.

## Important APIs, Types, and Functions

`struct gxp_spi` stores matched SoC data, three MMIO windows (`reg_base`, `dat_base`, `dir_base`), a device pointer, and per-CS `struct gxp_spi_chip` records. `gxp_spi_set_mode()` switches the controller between manual and direct mode. Register-like spi-mem operations are implemented by `gxp_spi_read_reg()` and `gxp_spi_write_reg()`. Addressed memory operations use `gxp_spi_read()` through the direct memory window and `gxp_spi_write()` through command/data registers. `do_gxp_exec_mem_op()` chooses the helper based on data direction and whether an address is present.

## Control Flow

Probe allocates a host, maps the register, data, and direct windows, stores match data, sets `mem_ops`, `setup`, and `num_chipselect`, then registers the controller. Per-device setup initializes the chip record and enters manual mode. A spi-mem operation with no address is treated as a command/register transaction: the driver programs chip select, opcode, length, direction, starts the controller, polls `SPIMCTRL_BUSY`, and copies data to or from `dat_base`. Addressed reads copy directly from `dir_base + op->addr.val`, with CS0 offset by `0x4000000`. Addressed writes program command/address/length, write up to the 256-byte data buffer, start, and poll completion.

## State and Persistence Behavior

The driver state is limited to mapped MMIO pointers and per-CS chip records. Persistent effects are flash-side effects from write and erase-related opcodes issued by the SPI NOR layer. The controller mode persists in hardware until changed by setup or another owner, but the driver does not maintain cached configuration beyond chip select.

## Dependencies and Integration Points

The driver integrates with the SPI memory API and platform/OF probing for `hpe,gxp-spifi`. It uses `readb_poll_timeout()`, MMIO byte/word/dword accessors, and SPI NOR-style `spi_mem_op` contracts. It does not expose generic `transfer_one`; it is intended for spi-mem flash users.

## Risks and Edge Cases

`gxp_spi_write()` truncates addressed writes to `SPILDAT_LEN` bytes and returns success for that chunk; correctness depends on spi-mem/NOR upper layers splitting writes appropriately or accepting short controller limits through other means. `gxp_spi_read()` returns `0` rather than byte count because `exec_op` status semantics use zero for success. There is no explicit `supports_op` or `adjust_op_size`, so invalid bus widths, dummy cycles, or too-large operations are not filtered locally. Timeout is a polling loop derived from `GXP_SPI_TIMEOUT`, and direct-window CS0 offset is a hardware-specific mapping that needs validation against flash layout.

## Test Signals

Validate probe with all three resources, both chip selects, RDID/RDSR/WRSR style no-address operations, direct reads across offsets and CS0 offset translation, page program sizes at and above 256 bytes, busy timeout injection, unsupported op shapes from spi-nor, and regression tests that ensure manual mode is entered before command-register accesses.
