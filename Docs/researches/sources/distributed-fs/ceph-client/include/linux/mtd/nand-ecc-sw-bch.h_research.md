# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-bch.h

## Purpose

Defines the software BCH ECC configuration and helper interface for NAND pages.

## Important APIs, Types, and Functions

Key type is `struct nand_ecc_sw_bch_conf`; exported helpers initialize/cleanup the BCH context, calculate ECC, correct data, and provide the software BCH engine when configured.

Source-visible symbols include structs: `struct nand_ecc_sw_bch_conf`, `struct nand_ecc_req_tweak_ctx req_ctx;`, `struct bch_control *bch;`, `struct nand_ecc_engine *nand_ecc_sw_bch_get_engine(void);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int nand_ecc_sw_bch_init_ctx(struct nand_device *nand);`, `void nand_ecc_sw_bch_cleanup_ctx(struct nand_device *nand);`; representative macros: `__MTD_NAND_ECC_SW_BCH_H__`.

## Control Flow

A NAND driver chooses BCH step size/strength, initializes a context, calculates ECC over outgoing data, and on reads compares read and calculated ECC to correct bitflips or report uncorrectable errors.

## State and Persistence Behavior

Runtime state is the BCH context, calculated/read ECC buffers, and ECC parameters. No persistent state exists beyond ECC bytes stored in flash OOB or interleaved layouts by callers.

## Dependencies and Integration Points

It depends on the generic NAND ECC engine contract, raw NAND glue, and kernel BCH support selected by config.

Direct includes observed in the source are: `#include <linux/mtd/nand.h>`, `#include <linux/bch.h>`.

## Risks and Edge Cases

The ECC byte count, OOB layout, strength, and step size must align. BCH can be CPU-expensive and must return MTD-compatible bitflip/error counts.

## Test Signals

Use deterministic BCH vectors, injected bitflips up to and above strength, erased-page cases, and disabled-config stub behavior.

Source read signal: 71 lines, 2117 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
