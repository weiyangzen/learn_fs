# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_micron.c

Purpose: this file implements Micron-specific raw NAND setup, especially ONFI vendor read-retry support and optional Micron on-die ECC integration for SLC parts with 4-bit or 8-bit correction per 512-byte step.

Important APIs, types, and functions: `micron_nand_manuf_ops` supplies `.init`, `.cleanup`, and `.fixup_onfi_param_page`. `struct micron_nand` stores on-die ECC state and a raw comparison buffer. `micron_nand_on_die_ecc_setup()`, `micron_nand_read_page_on_die_ecc()`, and `micron_nand_write_page_on_die_ecc()` become ECC engine callbacks. OOB layouts are split between 4-bit and 8-bit on-die ECC.

Control flow: init allocates manufacturer data, parses ONFI vendor read-retry count, sets SET/GET feature support bits, marks Micron BBM locations, detects on-die ECC by enabling/disabling the feature and checking READID bit 7, rejects mandatory on-die ECC unless the user selected `NAND_ECC_ENGINE_TYPE_ON_DIE`, and then wires ECC callbacks, OOB layout, ECC geometry, and raw-page restrictions.

State and persistence: `micron->ecc.enabled` tracks the current volatile ONFI on-die ECC feature state, and `forced` records parts where firmware/hardware cannot disable ECC. For 4-bit ECC, `rawbuf` temporarily stores raw page+OOB data so corrected and raw data can be compared to estimate bitflips.

Dependencies and integration points: this code depends on ONFI parameter/vendor pages, `nand_set_features()`/`nand_get_features()`, READID behavior, generic raw page helpers, MTD ECC statistics, OOB layout APIs, and selected ECC engine type from the NAND core.

Risks: mandatory on-die ECC is rejected for normal raw operation because raw access cannot be honored. 4-bit ECC bitflip accounting rereads the page with ECC disabled and compares buffers, so ordering and OOB availability matter. Status-based 8-bit accounting reports approximate correction counts. Detection has side effects because it toggles ECC during init.

Test signals: test ONFI revision fixup for zero revision, read-retry feature programming, on-die ECC selection/rejection, corrected/failed ECC stats for 4-bit and 8-bit status patterns, raw read/write behavior on mandatory ECC parts, OOB layout offsets, and cleanup of allocated raw buffers.
