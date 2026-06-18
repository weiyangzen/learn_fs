# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_hynix.c

## Purpose
`nand_hynix.c` implements Hynix-specific raw NAND detection and initialization. It decodes Hynix extended ID formats, derives OOB size and ECC requirements, marks devices that require scrambling, configures manufacturer-specific bad-block marker locations, sets up read-retry support for selected MLC parts from OTP data, and applies model-specific interface or pairing quirks.

## Important APIs, types, and functions
- Private structures are `struct hynix_nand`, `struct hynix_read_retry`, and `struct hynix_read_retry_otp`.
- Low-level command helpers are `hynix_nand_cmd_op()` and `hynix_nand_reg_write_op()`, both supporting `exec_op` and legacy command paths.
- Read-retry setup uses `hynix_read_rr_otp()`, `hynix_get_majority()`, `hynix_mlc_1xnm_rr_value()`, `hynix_mlc_1xnm_rr_init()`, `hynix_nand_rr_init()`, and `hynix_nand_setup_read_retry()`.
- ID decoding uses `hynix_nand_has_valid_jedecid()`, `hynix_nand_extract_oobsize()`, `hynix_nand_extract_ecc_requirements()`, `hynix_nand_extract_scrambling_requirements()`, and `hynix_nand_decode_id()`.
- Initialization and cleanup are `hynix_nand_init()` and `hynix_nand_cleanup()`, exported through `hynix_nand_manuf_ops`.
- Model-specific hooks include `h27ucg8t2atrbc_choose_interface_config()` and `h27ucg8t2etrbc_init()`.

## Control flow
Detection excludes SLC chips and short IDs from advanced Hynix decoding and falls back to `nand_decode_ext_id()`. For modern IDs, it decodes page size, eraseblock size, JEDEC-signature presence, OOB size, ECC requirements, and scrambling flags. Initialization sets BBM location flags based on SLC versus non-SLC, allocates `struct hynix_nand`, stores it as manufacturer data, applies model-specific quirks, and initializes read-retry support.

Read-retry initialization checks whether a valid JEDEC ID is present and whether the chip is MLC/TLC. For 1xnm technology, it reads an OTP area by entering Hynix parameter and OTP modes, reads the specified page, resets the chip back to normal, and decodes repeated values using majority voting. Successful decoding installs `chip->ops.setup_read_retry` and sets `chip->read_retries`; `nand_base.c` then uses this hook when ECC failures occur in `nand_do_read_ops()`.

## State and persistence behavior
The file allocates manufacturer-private heap state holding decoded read-retry tables and frees it in cleanup. It mutates chip options (`NAND_BBM_LASTPAGE`, `NAND_BBM_FIRSTPAGE`, `NAND_BBM_SECONDPAGE`, `NAND_NEED_SCRAMBLING`), ECC requirements, MTD geometry, pairing scheme, and optional interface-selection hooks. It writes volatile Hynix internal registers to change read-retry modes and to enter/exit OTP access; it does not intentionally persist user data or BBT contents.

## Dependencies and integration points
It depends on raw NAND operation helpers from `nand_base.c`, generic NAND geometry and ECC property APIs, MTD size macros, ONFI timing helpers, and the `dist3_pairing_scheme` exported by the core. It integrates through the Hynix manufacturer descriptor in `nand_ids.c`. Runtime read-retry integration is via `chip->ops.setup_read_retry`, consumed by the generic read loop after ECC failures.

## Risks and edge cases
- `hynix_get_majority()` only accepts values appearing more than half the time; marginal OTP reads can fail initialization and leave read-retry unavailable.
- The OTP initialization loop appears intended to try multiple OTP layouts, but the call passes `hynix_mlc_1xnm_rr_otps` rather than `&hynix_mlc_1xnm_rr_otps[i]`, so only the first layout is effectively used.
- Register command sequences are vendor-private and sensitive to target selection and current interface state.
- OOB-size and ECC decoding branch on whether a JEDEC signature is present; misclassification changes geometry and can corrupt addressing.
- Scrambling and pairing quirks are model/process dependent; missing a model can produce unstable reads on high-density MLC/TLC parts.

## Test signals
Validation should include SLC fallback decoding, legacy Hynix extended IDs, JEDEC-signature Toggle DDR IDs, OOB-size scaling for 16KiB-page `0xde` devices, ECC-level mappings for both valid-JEDEC and non-JEDEC paths, TLC/MLC scrambling flags, H27UCG8T2ATR-BC interface selection, H27UCG8T2ETR-BC pairing scheme and scrambling, read-retry OTP success and failure, and generic read-loop recovery after an ECC failure.
