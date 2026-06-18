# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-sw-hamming.h

## Purpose

Defines software Hamming ECC support for NAND, including layout/order options and engine access.

## Important APIs, Types, and Functions

It provides `struct nand_ecc_sw_hamming_conf`, raw NAND calculation/correction hooks, cleanup, and `nand_ecc_sw_hamming_get_engine()` when enabled.

Source-visible symbols include structs: `struct nand_ecc_sw_hamming_conf`, `struct nand_ecc_req_tweak_ctx req_ctx;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int nand_ecc_sw_hamming_init_ctx(struct nand_device *nand);`, `void nand_ecc_sw_hamming_cleanup_ctx(struct nand_device *nand);`; representative macros: `__MTD_NAND_ECC_SW_HAMMING_H__`.

## Control Flow

Raw NAND code initializes Hamming parameters, calculates 3-byte-style ECC per step on writes, and corrects single-bit errors or reports uncorrectable conditions on reads. SmartMedia byte-order mode is represented by options.

## State and Persistence Behavior

State is a small per-chip context and ECC buffers; persistent bytes are stored by the caller in OOB according to the selected layout.

## Dependencies and Integration Points

It integrates with raw NAND ECC callbacks and the generic NAND ECC engine.

Direct includes observed in the source are: `#include <linux/mtd/nand.h>`.

## Risks and Edge Cases

Wrong byte ordering or OOB position breaks compatibility with existing media. Hamming strength is limited and must not be over-advertised.

## Test Signals

Single-bit correction vectors, double-bit failure vectors, SmartMedia order compatibility, and erased-page behavior.

Source read signal: 89 lines, 2714 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
