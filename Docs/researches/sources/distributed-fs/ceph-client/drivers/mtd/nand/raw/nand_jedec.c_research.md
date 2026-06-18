# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_jedec.c

## Purpose
`nand_jedec.c` detects JEDEC-compliant raw NAND devices and fills generic NAND/MTD geometry, feature, bus-width, and ECC requirement state from the JEDEC parameter page.

## Important APIs, types, and functions
- `nand_jedec_detect(struct nand_chip *chip)` is the single exported detector called by `nand_detect()` after ONFI detection fails.
- The function uses `nand_readid_op()` at address `0x40` to check for the `"JEDEC"` signature.
- It reads up to `JEDEC_PARAM_PAGES` copies of `struct nand_jedec_params`, validates each with `onfi_crc16()`, and uses `nand_read_param_page_op()`, `nand_read_data_op()`, or `nand_change_read_column_op()` depending on controller capabilities.
- It sanitizes and stores the model string, marks read-cache support, fills `nand_memory_organization`, updates MTD writesize/erasesize/OOB size, sets 16-bit bus options, and derives ECC requirements from `struct jedec_ecc_info`.

## Control flow
The detector first checks the JEDEC signature. If absent or unreadable, it returns 0 so generic detection can continue. On signature match it allocates a parameter-page buffer, decides whether repeated parameter pages can be read as data-only operations, reads up to three parameter pages, and stops at the first valid CRC. It then validates the revision bits, extracts model and feature fields, fills geometry and organization values, sets bus-width flags, records ECC requirements if the codeword size is valid, frees the temporary page, and returns 1 for successful detection.

## State and persistence behavior
The file allocates only a temporary parameter-page buffer and a duplicated model string retained in `chip->parameters.model` until scan cleanup. It mutates in-memory chip, MTD, and NAND-device geometry and ECC requirement state. It does not write NAND flash and has no persistent side effects.

## Dependencies and integration points
It depends on raw NAND command helpers from `nand_base.c`, ONFI CRC/string helpers, JEDEC parameter structures from raw NAND internals, and generic ECC property APIs. It is integrated into `nand_detect()` after ONFI and before table/manufacturer fallback completes for unknown devices.

## Risks and edge cases
- If all redundant parameter-page CRCs fail, detection aborts for the JEDEC path and returns 0 after logging an error.
- Unsupported revision bits also return 0, allowing later fallback but losing JEDEC-derived geometry.
- Geometry uses power-of-two rounding for pages per block and blocks per LUN, matching ONFI handling but potentially hiding non-power-of-two advertised values.
- Invalid ECC codeword sizes only warn, leaving ECC requirements unset and pushing selection to defaults or controller/user configuration.
- Data-only reads are preferred when the controller supports them; otherwise column changes must be correctly implemented for repeated parameter-page reads.

## Test signals
Validation should cover absent JEDEC signatures, valid signature with first/second/third parameter-page CRC success, all-CRC failure, unsupported revision values, read-cache option extraction, 16-bit bus feature extraction, ECC codeword size mapping, data-only versus change-column parameter reads, and cleanup on allocation or read failure.
