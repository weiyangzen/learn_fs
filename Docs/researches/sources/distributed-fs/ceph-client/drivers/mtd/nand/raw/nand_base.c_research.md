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
