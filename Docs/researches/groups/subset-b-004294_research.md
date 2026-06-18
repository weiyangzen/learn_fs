# Research group subset-b-004294

Grouped research for raw NAND files under `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_base.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_base.c

## Purpose
`nand_base.c` is the generic raw NAND core for the MTD stack. It bridges `struct nand_chip`, `struct nand_device`, controller `exec_op` hooks, legacy command hooks, ECC engines, bad-block handling, device-tree options, identification, scan/attach, and MTD callbacks. It is the central implementation used by controller drivers after they populate chip/controller hooks and call `nand_scan_with_ids()`.

## Important APIs, types, and functions
- Exported command helpers include `nand_select_target()`, `nand_deselect_target()`, `nand_read_page_op()`, `nand_change_read_column_op()`, `nand_read_oob_op()`, `nand_prog_page_begin_op()`, `nand_prog_page_end_op()`, `nand_prog_page_op()`, `nand_change_write_column_op()`, `nand_readid_op()`, `nand_status_op()`, `nand_exit_status_op()`, `nand_erase_op()`, `nand_reset_op()`, `nand_read_data_op()`, and `nand_write_data_op()`. These provide chip-command primitives for raw NAND controller and manufacturer code.
- Operation parser helpers (`nand_op_parser_exec_op()`, `nand_subop_get_addr_start_off()`, `nand_subop_get_num_addr_cyc()`, `nand_subop_get_data_start_off()`, `nand_subop_get_data_len()`) split abstract NAND operations into controller-supported suboperations.
- MTD data paths are implemented by `nand_read_oob()`, `nand_write_oob()`, `nand_erase()`, `nand_block_isbad()`, `nand_block_markbad()`, `nand_suspend()`, `nand_resume()`, `nand_lock()`, and `nand_unlock()`.
- ECC helpers cover raw, software Hamming, software BCH, on-host hardware ECC, syndrome layouts, subpage reads/writes, erased-page checks, and selection via `nand_ecc_choose_conf()`.
- Identification and scan helpers include `nand_detect()`, `nand_decode_ext_id()`, `nand_decode_id()`, `nand_manufacturer_detect()`, `rawnand_dt_init()`, `nand_scan_ident()`, `nand_scan_tail()`, `nand_scan_with_ids()`, and `nand_cleanup()`.
- Internal state is mostly on `struct nand_chip`: target selection (`cur_cs`), locking and suspend state, page cache, ECC controller function table, OOB/data buffers, interface timings, BBT options/table, secure regions, manufacturer data, and read-retry state.

## Control flow
Probe starts in `nand_scan_with_ids()`, which runs `nand_scan_ident()`, controller `attach_chip`, and `nand_scan_tail()`. Identification initializes locks and reset timings, parses DT, installs defaults, reads and verifies the NAND ID twice, selects table/ONFI/JEDEC/manufacturer decoding, computes geometry shifts and row-address width, then counts matching targets. Tail setup allocates the data/OOB buffer, calls manufacturer init while target 0 is selected, chooses OOB layout and ECC operations, initializes the generic NAND device, assigns MTD callbacks, chooses and applies the best interface timing on every target, parses secure regions, and creates the bad-block table unless scanning is disabled.

Read flow enters through `nand_read_oob()`, takes the chip/controller locks with `nand_get_device()`, and routes either to `nand_do_read_oob()` or `nand_do_read_ops()`. Data reads select the target, compute page/column, optionally enable continuous cached reads, use a bounce buffer for unaligned or DMA-unsafe buffers, choose raw/subpage/full-page ECC helpers, transfer OOB if requested, wait for ready when required, retry pages through manufacturer `setup_read_retry`, update `ops->retlen` and ECC stats, and clear continuous-read state before returning.

Write flow enters through `nand_write_oob()`, validates OOB mode, locks the device, and calls `nand_do_write_oob()` or `nand_do_write_ops()`. Data writes require subpage alignment, reject secure regions, select the target, check write-protect, invalidate the page cache, stage partial writes or DMA-unsafe buffers in `chip->data_buf`, fill OOB with caller data or `0xff`, call `nand_write_page()`, and advance across pages and targets.

Erase flow uses `nand_erase_nand()`: block alignment and secure-region checks precede locking, target selection, write-protect checks, bad-block refusal, page-cache invalidation, and `nand_erase_op()` per eraseblock. `nand_block_markbad_lowlevel()` erases before writing OOB BBM unless disabled, then updates the flash/RAM BBT and ECC bad-block counters.

## State and persistence behavior
The persistent state affected by this file is NAND flash data, OOB metadata, erase state, on-flash BBT contents through `nand_bbt.c`, bad-block markers, and optional secure-region access policy parsed from DT. Runtime-only state includes the page cache (`chip->pagecache`), best/current interface timing, `cont_read` window, ECC buffers, manufacturer-private data, and lock/suspend flags. BBT and bad-block marker updates are persistent and intentionally serialized through the chip/controller locks, but the file comment still notes that BBT table serialization has historical limitations.

## Dependencies and integration points
This file depends on the Linux MTD core, raw NAND internals, ONFI/JEDEC helpers, ECC software libraries, GPIO descriptors, OF/device-tree parsing, controller `struct nand_controller_ops`, manufacturer ops from `nand_ids.c`, and BBT APIs from `nand_bbt.c`. Controller drivers integrate by filling `chip->controller`, `chip->legacy` or `exec_op`, ECC hooks/caps, optional `attach_chip`/`detach_chip`, and then invoking scan. Manufacturer drivers integrate through `detect`, `init`, `cleanup`, `setup_read_retry`, `fixup_onfi_param_page`, and interface-config hooks.

## Risks and edge cases
- Geometry and bus-width detection are fragile because wrong ID decoding leads to wrong page/block/OOB shifts and destructive command addressing.
- Secure regions are protected by software checks in read/write/OOB/erase/BBM paths; controller- or boot-time accesses outside this path could bypass that policy.
- Continuous cached reads are disabled for on-die ECC and read-retry devices, but still depend on correct LUN boundary calculations and controller support checks.
- Partial writes rely on erased `0xff` bounce buffers and OOB masking, which can be unsafe on NANDs that disallow partial programming.
- ECC fallback and maximization can silently change selected algorithms when requested settings are impossible; mismatches surface as warnings or probe failures depending on mode.
- `nand_get_device()` waits for resume and then takes both chip and controller locks, so new call sites must avoid lock-order inversions with controller callbacks.
- Several helpers support both `exec_op` and legacy hooks; changes must preserve both paths until legacy controller support is removed.

## Test signals
Useful validation includes probe tests with ONFI, JEDEC, full-ID, extended-ID, and manufacturer-specific devices; multi-target detection; 8-bit and 16-bit bus devices; small-page and large-page devices; raw, software Hamming, software BCH, on-host ECC, on-die ECC, and syndrome layouts; MTD read/write/OOB/erase paths across target boundaries; bad-block mark/isbad behavior with and without flash BBT; read-retry recovery after ECC failures; suspend/resume blocking; secure-region rejection; and controller `exec_op` parser check-only plus split-operation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_bbt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_bbt.c

## Purpose
`nand_bbt.c` implements bad-block table support for the raw NAND core. It scans factory bad-block markers, creates the in-memory two-bit-per-block BBT, finds or writes flash-resident BBTs and mirrors, marks BBT storage blocks as reserved, and exposes query/update APIs used by `nand_base.c`.

## Important APIs, types, and functions
- The in-memory table uses two bits per eraseblock with internal values `BBT_BLOCK_GOOD`, `BBT_BLOCK_WORN`, `BBT_BLOCK_RESERVED`, and `BBT_BLOCK_FACTORY_BAD`.
- Public APIs are `nand_create_bbt()`, `nand_isreserved_bbt()`, `nand_isbad_bbt()`, and `nand_markbad_bbt()`.
- Scanning helpers include `scan_block_fast()`, `create_bbt()`, `search_bbt()`, `search_read_bbts()`, and `nand_memory_bbt()`.
- Flash BBT helpers include `read_bbt()`, `read_abs_bbt()`, `read_abs_bbts()`, `get_bbt_block()`, `write_bbt()`, `check_create()`, `nand_update_bbt()`, and `mark_bbt_region()`.
- Descriptor setup is handled by `nand_create_badblock_pattern()` plus the default main/mirror descriptors for OOB and no-OOB BBT markers.

## Control flow
`nand_create_bbt()` selects default flash BBT descriptors when `NAND_BBT_USE_FLASH` is set, otherwise forces a RAM-only table. It ensures a bad-block marker descriptor exists and then calls `nand_scan_bbt()`. `nand_scan_bbt()` allocates the RAM BBT, either scans the device directly when no flash descriptor exists, or searches/reads flash BBT descriptors, reconciles missing or stale mirrors through `check_create()`, and reserves BBT regions.

When creating a RAM table, `create_bbt()` walks eraseblocks, reads configured BBM pages through `scan_block_fast()`, and records factory-bad entries. When using flash BBTs, `search_bbt()` searches candidate blocks from the start or end, skips blocks that are bad or conflict with marker areas, validates marker patterns, and records pages and versions. `check_create()` compares primary and mirror versions, decides whether to create, read, rewrite, or scrub tables, reads valid tables into RAM, and writes missing/stale copies.

`write_bbt()` serializes the RAM BBT to flash using the descriptor bit width and reserved-block code. It can preserve block contents, store the marker in the data area for `NAND_BBT_NO_OOB`, write marker/version in OOB otherwise, erase the destination with BBT access allowed, write data plus OOB, and mark failed BBT blocks as worn before retrying another reserved block.

## State and persistence behavior
The primary runtime state is `this->bbt`, a compact RAM bitmap of eraseblock states. Persistent state can be OOB bad-block markers and optional flash BBT blocks, including mirrored versions. Descriptor arrays store selected pages and per-chip versions. `nand_markbad_bbt()` updates the RAM entry and then updates on-flash BBTs when `NAND_BBT_USE_FLASH` is enabled. `mark_bbt_region()` marks BBT storage blocks as reserved in RAM and may write that reservation back to flash when the descriptor carries a reserved-block code.

## Dependencies and integration points
The file depends on MTD read/write/OOB/erase APIs, raw NAND geometry from `struct nand_chip`, marker-page iteration from `nand_bbm_get_next_page()`, bad-block marker writes from `nand_markbad_bbm()`, erase from `nand_erase_nand()`, and expert-analysis behavior from the MTD layer. `nand_base.c` uses these APIs for `block_isbad`, `block_isreserved`, bad-block marking, and scan-tail BBT creation.

## Risks and edge cases
- Flash BBT version comparison uses signed byte subtraction semantics, so wraparound behavior must remain intentional.
- `NAND_BBT_NO_OOB` descriptors have strict constraints; invalid descriptor combinations trigger `BUG_ON()`.
- A failed erase/write of a BBT block marks that block bad and retries, which is correct for flash health but destructive if geometry or descriptor placement is wrong.
- Scanning ignores ECC failures when checking BBM OOB patterns, but ECC errors while reading flash BBTs can invalidate tables and force fallback paths.
- RAM table entries use OR-style marking, so state transitions only add bits; callers must not expect a simple overwrite from bad/reserved back to good.
- The expert analysis mode can report bad/reserved blocks as usable, which is useful diagnostically but risky in normal deployments.

## Test signals
Validation should cover RAM-only BBT creation, flash BBT with and without mirrors, per-chip BBTs, absolute-page descriptors, OOB and no-OOB marker placement, version mismatch and missing mirror repair, bitflip-triggered BBT scrubbing, BBT storage block failures, reserved-block handling, 8-bit and 16-bit BBM descriptors, expert-analysis mode, and `nand_markbad_bbt()` persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_bbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_esmt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_esmt.c

## Purpose
`nand_esmt.c` provides ESMT manufacturer hooks for the raw NAND core. It customizes extended-ID decoding for SLC ESMT parts by extracting ECC requirements from the fifth ID byte and broadens bad-block marker scanning for known ESMT SLC marker placement variance.

## Important APIs, types, and functions
- `esmt_nand_decode_id()` calls the generic `nand_decode_ext_id()` and then, for SLC chips with at least five ID bytes, maps `chip->id.data[4] & 0x3` to ECC requirements of 4, 2, or 1 bit per 512-byte step.
- `esmt_nand_init()` sets `NAND_BBM_FIRSTPAGE`, `NAND_BBM_SECONDPAGE`, and `NAND_BBM_LASTPAGE` for SLC chips.
- `esmt_nand_manuf_ops` exports `.detect` and `.init` hooks to the manufacturer descriptor table in `nand_ids.c`.

## Control flow
During non-ONFI/non-JEDEC manufacturer detection, `nand_base.c` calls the ESMT `.detect` hook through the manufacturer descriptor. The hook first derives normal geometry through generic extended-ID decoding, then updates `nand_device` ECC requirements. Later, scan-tail manufacturer initialization calls `.init`, where SLC chips opt into checking all three common BBM locations before BBT creation.

## State and persistence behavior
The file does not allocate private state and has no cleanup hook. It mutates in-memory chip/device state: ECC requirement properties and `chip->options` BBM flags. Those flags affect later persistent behavior indirectly because BBT scans and bad-block marking may read or write markers in first, second, and last block pages.

## Dependencies and integration points
It depends on `nand_decode_ext_id()`, `nand_is_slc()`, `nanddev_set_ecc_requirements()`, and the raw NAND manufacturer-ops dispatch. Its only external integration is the `NAND_MFR_ESMT` entry in `nand_ids.c`.

## Risks and edge cases
- The ECC mapping is only applied to SLC chips with at least five ID bytes; other ESMT parts fall back to generic requirements.
- An unknown ECC code triggers `WARN(1)` and clears the requirement step size, which may force later ECC selection to maximize or use user/controller defaults.
- Checking first, second, and last BBM pages is conservative but may classify blocks bad if any one of the scanned locations contains non-`0xff` metadata on unusual layouts.

## Test signals
Useful tests include ESMT SLC IDs with fifth-byte ECC codes 0, 1, 2, and 3; BBT scanning against first-page, second-page, and last-page factory markers; non-SLC ESMT detection; and probe behavior when ECC requirements are absent and controller ECC caps must choose a fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_esmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_hynix.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_hynix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_ids.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_ids.c

## Purpose
`nand_ids.c` is the raw NAND static identification database. It contains legacy, extended-ID, and selected full-ID NAND descriptors plus the manufacturer-ID table that connects manufacturer IDs to optional manufacturer operations.

## Important APIs, types, and functions
- `nand_flash_ids[]` is the exported chip table consumed by `nand_detect()` when no controller-specific table is supplied.
- Full-ID entries describe devices whose shared device IDs are not sufficient; they include exact ID byte arrays, geometry, options, ID length, OOB size, and ECC requirements.
- `LEGACY_ID_NAND()` and `EXTENDED_ID_NAND()` entries cover older small-page devices and density-coded large-page devices where geometry is decoded from ID bytes.
- `nand_manufacturer_descs[]` maps manufacturer constants such as AMD/Spansion, ESMT, Hynix, Macronix, Micron, Samsung, SanDisk, Toshiba, and others to names and optional `nand_manufacturer_ops`.
- `nand_get_manufacturer_desc(u8 id)` linearly searches the descriptor table and returns a matching manufacturer descriptor or `NULL`.

## Control flow
During `nand_detect()`, the raw NAND core reads ID bytes, stores the manufacturer descriptor from `nand_get_manufacturer_desc()`, and walks `nand_flash_ids[]`. Full-ID entries are tried first, which lets the core match specific incompatible devices before falling back to generic device-ID entries. If no fixed-size table entry fully identifies the chip, the core tries ONFI, JEDEC, and manufacturer-specific extended-ID decoding.

## State and persistence behavior
This file is static data plus one lookup function. It does not allocate memory, mutate runtime state directly, or persist anything. Its descriptors indirectly determine runtime geometry, ECC requirements, options such as bus width or scrambling, and manufacturer hook selection during scan.

## Dependencies and integration points
It depends on `internals.h` for NAND descriptor macros, constants, and manufacturer ops declarations. It integrates with `nand_base.c` identification, ONFI/JEDEC fallback logic, and manufacturer-specific files such as ESMT and Hynix. The descriptor order is part of behavior: full-ID devices must precede generic shared-ID entries.

## Risks and edge cases
- Incorrect geometry, OOB size, or ECC requirement data in a table entry can cause destructive misaddressing or insufficient ECC.
- Adding a generic entry before a more specific full-ID entry could prevent the specific match.
- Manufacturer descriptors without ops still provide names but leave decoding to generic mechanisms.
- Full-ID entries using `NAND_NEED_SCRAMBLING` or high ECC requirements are board-critical; omitting these options can produce unreliable reads.

## Test signals
Tests should verify full-ID precedence, fallback to legacy/extended-ID entries, manufacturer descriptor lookup for known and unknown IDs, detection with a controller-provided alternate table, and probe logs/geometry for the listed special devices. Static build coverage should catch missing manufacturer ops declarations when descriptors reference vendor hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_ids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_jedec.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_jedec.c -->
