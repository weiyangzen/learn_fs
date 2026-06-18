# sources/distributed-fs/ceph-client/include/linux/mtd/spi-nor.h

## Purpose

Defines the SPI NOR core public contract: standard opcodes/status bits, SPI protocol encodings, controller capability masks, controller operations, command-extension modes, and `struct spi_nor` state.

## Important APIs, Types, and Functions

Important APIs include opcode/status macros, `enum spi_nor_protocol`, protocol-width helpers, `struct spi_nor_hwcaps`, capability masks, `struct spi_nor_controller_ops`, `enum spi_nor_cmd_ext`, `struct spi_nor`, flash-node accessors, and `spi_nor_scan()`.

Source-visible symbols include structs: `struct spi_nor_hwcaps`, `struct spi_nor;`, `struct spi_nor_controller_ops`, `struct flash_info;`, `struct spi_nor_manufacturer;`, `struct spi_nor_flash_parameter;`, `struct spi_nor`, `struct mtd_info		mtd;`, `struct mutex		lock;`, `struct spi_nor_rww`, `struct device		*dev;`, `struct spi_mem		*spimem;`; enums: `enum spi_nor_protocol`, `enum spi_nor_cmd_ext`, `enum spi_nor_protocol	read_proto;`, `enum spi_nor_protocol	write_proto;`, `enum spi_nor_protocol	reg_proto;`, `enum spi_nor_cmd_ext	cmd_ext_type;`; typedefs: none visible in this header; prototypes: `return spi_nor_get_protocol_data_nbits(proto);`, `return mtd_get_of_node(&nor->mtd);`; representative macros: `__LINUX_MTD_SPI_NOR_H`, `SPINOR_OP_READ_1_1_1_DTR`, `SPINOR_OP_READ_1_2_2_DTR`, `SPINOR_OP_READ_1_4_4_DTR`, `SPINOR_OP_READ_1_1_1_DTR_4B`, `SPINOR_OP_READ_1_2_2_DTR_4B`, `SPINOR_OP_READ_1_4_4_DTR_4B`, `SR_E_ERR`, `SR_P_ERR`, `SR1_QUAD_EN_BIT6`, `SR_BP_SHIFT`, `SR2_QUAD_EN_BIT1`, `SR2_QUAD_EN_BIT7`, `SNOR_PROTO_INST_MASK`, `SNOR_PROTO_INST_SHIFT`, `SNOR_PROTO_INST`.

## Control Flow

Controller drivers supply register/data read/write/erase operations and hardware capability masks. `spi_nor_scan()` identifies the flash, parses SFDP/fixups, fills opcodes/protocols/address width/erase parameters, sets MTD callbacks, and may use spi-mem dirmap descriptors for data paths.

## State and Persistence Behavior

Runtime state includes embedded `mtd_info`, lock, read-while-write synchronization state, SPI device handles, DMA bounce buffer, JEDEC ID, manufacturer/info pointers, address bytes, selected opcodes, protocol modes, flags, command-extension type, SFDP data, debugfs root, controller ops, flash parameters, dirmaps, and private data.

## Dependencies and Integration Points

It depends on MTD core, bit operations, and SPI memory APIs. It integrates with SPI NOR manufacturer/fixup tables, SFDP parsing, MTD partition registration, and SPI controller drivers.

Direct includes observed in the source are: `#include <linux/bitops.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/spi/spi-mem.h>`.

## Risks and Edge Cases

Capability priority controls high-speed protocol selection; wrong quad/octal/DTR enablement or 4-byte addressing can make data inaccessible. RWW synchronization must serialize reads/program/erase per bank.

## Test Signals

Scan common JEDEC/SFDP parts, protocol capability negotiation, 3-byte/4-byte addressing, quad/octal/DTR register handling, lock/unlock/security registers, bounce-buffer paths, dirmap reads/writes, and RWW contention.

Source read signal: 453 lines, 16734 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
