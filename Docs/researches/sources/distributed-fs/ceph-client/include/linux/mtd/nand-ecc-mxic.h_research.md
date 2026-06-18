# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mxic.h

## Purpose

Defines the Macronix NAND ECC engine interface used by host drivers that offload ECC to a Macronix block.

## Important APIs, Types, and Functions

It exposes opaque `struct mxic_ecc_engine`, config structures, and helper calls to get/put the engine, enable/disable operations, process pages, and retrieve ECC status.

Source-visible symbols include structs: `struct mxic_ecc_engine;`, `struct nand_ecc_engine *mxic_ecc_get_pipelined_engine(struct platform_device *spi_pdev);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `void mxic_ecc_put_pipelined_engine(struct nand_ecc_engine *eng);`, `return ERR_PTR(-EOPNOTSUPP);`; representative macros: `__MTD_NAND_ECC_MXIC_H__`.

## Control Flow

The host initializes an ECC configuration, enables the engine for read or write, runs data through the hardware pipeline, waits/collects status, then disables the engine before returning data to MTD/NAND core.

## State and Persistence Behavior

State is transient hardware and per-request ECC configuration/status. Persistent flash layout is determined by the caller's OOB/ECC placement.

## Dependencies and Integration Points

It integrates with the generic NAND ECC engine model and Macronix controller code. Correct use depends on `nand_device`/`mtd_info` geometry and OOB layout choices.

Direct includes observed in the source are: `#include <linux/platform_device.h>`, `#include <linux/device.h>`.

## Risks and Edge Cases

Risks are unsupported geometry, wrong OOB placement, missed error propagation, and shared-engine lifetime mistakes.

## Test Signals

Exercise get/put, enable/disable, clean decode, corrected bitflips, uncorrectable pages, and geometry rejection.

Source read signal: 49 lines, 1353 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
