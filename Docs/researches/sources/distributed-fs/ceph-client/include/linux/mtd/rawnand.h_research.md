# sources/distributed-fs/ceph-client/include/linux/mtd/rawnand.h

## Purpose

Defines MTD-related contracts for `rawnand.h`.

## Important APIs, Types, and Functions

The important API surface is captured by the source-derived symbol inventory below.

Source-visible symbols include structs: `struct nand_chip;`, `struct gpio_desc;`, `struct nand_parameters`, `struct onfi_params *onfi;`, `struct nand_id`, `struct nand_ecc_step_info`, `struct nand_ecc_caps`, `struct nand_ecc_ctrl`, `struct nand_sdr_timings`, `struct nand_nvddr_timings`, `struct nand_interface_config`, `struct nand_timings`; enums: `enum nand_ecc_engine_type engine_type;`, `enum nand_ecc_placement placement;`, `enum nand_ecc_algo algo;`, `enum nand_interface_type`, `enum nand_interface_type type;`, `enum nand_op_instr_type`, `enum nand_op_instr_type type;`; typedefs: none visible in this header; prototypes: `return ERR_PTR(-EINVAL);`, `return ERR_PTR(-EINVAL);`, `return container_of(mtd, struct nand_chip, base.mtd);`, `return mtd_get_of_node(nand_to_mtd(chip));`, `int nand_create_bbt(struct nand_chip *chip);`, `int rawnand_sw_hamming_init(struct nand_chip *chip);`, `void rawnand_sw_hamming_cleanup(struct nand_chip *chip);`, `int rawnand_sw_bch_init(struct nand_chip *chip);`, `void rawnand_sw_bch_cleanup(struct nand_chip *chip);`, `int nand_write_oob_std(struct nand_chip *chip, int page);`, `int nand_read_oob_std(struct nand_chip *chip, int page);`, `int nand_reset(struct nand_chip *chip, int chipnr);`, `int nand_reset_op(struct nand_chip *chip);`, `int nand_status_op(struct nand_chip *chip, u8 *status);`; representative macros: `__LINUX_MTD_RAWNAND_H`, `NAND_MAX_CHIPS`, `NAND_NCE`, `NAND_CLE`, `NAND_ALE`, `NAND_CTRL_CLE`, `NAND_CTRL_ALE`, `NAND_CTRL_CHANGE`, `NAND_CMD_READ0`, `NAND_CMD_READ1`, `NAND_CMD_RNDOUT`, `NAND_CMD_PAGEPROG`, `NAND_CMD_READOOB`, `NAND_CMD_ERASE1`, `NAND_CMD_STATUS`, `NAND_CMD_SEQIN`.

## Control Flow

Control flow is implemented by including drivers; this header supplies the constants, structures, or prototypes those drivers use.

## State and Persistence Behavior

State behavior is limited to the fields declared here and any hardware/media state represented by constants.

## Dependencies and Integration Points

Dependencies are visible from the include list and neighboring MTD subsystem headers.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nand.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/bbm.h>`, `#include <linux/mtd/jedec.h>`, `#include <linux/mtd/onfi.h>`, `#include <linux/mutex.h>`, `#include <linux/of.h>`.

## Risks and Edge Cases

Risks center on ABI/layout drift and callers misinterpreting the declared constants or callback contracts.

## Test Signals

Build coverage plus targeted driver tests should exercise the declared symbols.

Source read signal: 1640 lines, 53764 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
