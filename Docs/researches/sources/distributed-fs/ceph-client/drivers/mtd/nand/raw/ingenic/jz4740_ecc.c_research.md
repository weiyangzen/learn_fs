# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4740_ecc.c

Purpose: this is the Ingenic JZ4740 Reed-Solomon ECC provider. It implements the common Ingenic ECC ops for the older JZ4740 NAND ECC block, including special erased-page ECC handling.

Important APIs, types, and functions: key functions are `jz4740_ecc_reset()`, `jz4740_ecc_calculate()`, `jz_nand_correct_data()`, `jz4740_ecc_correct()`, and `jz4740_ecc_disable()`. The provider registers `jz4740_ecc_ops` through compatible `ingenic,jz4740-ecc`. `empty_block_ecc` encodes the hardware parity pattern produced for all-0xff data.

Control flow: calculate resets the ECC block in encoding mode, polls `JZ_NAND_STATUS_ENC_FINISH`, disables the block, reads parity bytes from the parity registers, and rewrites the known all-FF parity pattern to 0xff bytes for subpage-write compatibility. Correct resets in decode mode, writes the read ECC bytes to parity registers, marks parity ready, polls decode finish, disables the block, returns `-EBADMSG` for uncorrectable status, or reads error records and applies `jz_nand_correct_data()` for in-range data errors.

State and persistence: the driver uses only hardware register state and the common provider state from `ingenic_ecc`. Unlike the BCH providers, calculate/correct do not explicitly lock `ecc->lock`; serialization is therefore provided only by higher layers and the NAND request path, not by this file.

Dependencies and integration points: the file depends on the common Ingenic ECC API, platform OF matching, MMIO accessors, and raw NAND ECC callback flow through `ingenic_nand_drv.c`.

Risks: polling loops use a hard-coded iteration count of 1000 without delay, so timeout behavior is CPU-speed dependent. Lack of local mutex locking differs from the JZ4725B/JZ4780 BCH providers. `jz_nand_correct_data()` rewrites a 9-bit span around an index and must match the hardware error encoding exactly. The provider assumes the caller has selected 9 ECC bytes for JZ4740 strength-4 operation.

Test signals: verify ECC bytes for normal and all-FF buffers, single and multiple correctable bit errors, uncorrectable error reporting, decode timeout behavior, and integration with the JZ4740 NAND path using OOB-first hardware-ECC page reads.
