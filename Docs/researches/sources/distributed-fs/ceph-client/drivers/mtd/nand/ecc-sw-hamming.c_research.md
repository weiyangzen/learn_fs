# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-hamming.c

Purpose: implements the generic software Hamming ECC engine for 256- or 512-byte NAND ECC steps, correcting one data bit and detecting common multi-bit errors.

Important APIs and types: exported low-level functions are `ecc_sw_hamming_calculate()` and `ecc_sw_hamming_correct()`. NAND-facing exports are `nand_ecc_sw_hamming_calculate()`, `nand_ecc_sw_hamming_correct()`, `nand_ecc_sw_hamming_init_ctx()`, `nand_ecc_sw_hamming_cleanup_ctx()`, and `nand_ecc_sw_hamming_get_engine()`. Lookup tables `invparity`, `bitsperbyte`, and `addressbits` drive parity and correction decoding.

Control flow: calculation folds the data buffer into row and column parity values, handles endian differences, optionally emits SmartMedia byte order, and produces three ECC bytes per step. Correction XORs read and calculated ECC, distinguishes no error, single data-bit error, single ECC-bit error, and uncorrectable error, flipping the addressed data bit when possible. Context init installs default small-page or legacy large-page Hamming OOB layouts, chooses 256-byte steps unless the user explicitly selects 512, allocates request tweak and OOB buffers, and sets strength to 1. Prepare and finish mirror the BCH engine: raw/data-less requests are no-ops, writes calculate and place ECC bytes, reads extract OOB ECC, correct data per step, update ECC stats, and restore tweaked requests.

State and persistence: runtime state is the per-device Hamming config and temporary buffers. Persistent state is the three ECC bytes per step in the configured OOB layout.

Dependencies and integration points: selected by generic ECC code for `NAND_ECC_ALGO_HAMMING`; depends on MTD OOB layout helpers, request tweaking, optional `CONFIG_MTD_NAND_ECC_SW_HAMMING_SMC` behavior through config data, and legacy NAND OOB conventions.

Risks and test signals: risks include byte-order compatibility, 256 versus 512 step addressing, unaligned buffers, OOB layout mismatch, and correct classification of ECC-bit-only errors. Tests should cover known ECC vectors, single-bit corrections across first/last byte and bit, single ECC-bit error, double-bit uncorrectable error, SmartMedia ordering, raw mode, small and large OOB layouts, and request bounce restoration.
