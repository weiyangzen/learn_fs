<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_test.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_test.c

## Purpose
`mmc_test.c` implements the optional MMC/SD host test driver exposed through debugfs. It claims cards for destructive and performance-oriented testing, runs a catalog of transfer, alignment, partial-block, highmem, erase/trim, random/sequential, retuning, reset, non-blocking, and command-during-transfer tests, and records results for later debugfs reads.

## Important APIs, Types, And Functions
Key structs are `mmc_test_card`, `mmc_test_area`, `mmc_test_mem`, `mmc_test_pages`, `mmc_test_req`, `mmc_test_case`, `mmc_test_general_result`, `mmc_test_transfer_result`, and `mmc_test_dbgfs_file`. Main lifecycle functions are `mmc_test_probe()`, `mmc_test_remove()`, `mmc_test_init()`, `mmc_test_exit()`, `mmc_test_register_dbgfs_file()`, `mtf_test_write()`, `mtf_test_show()`, and `mtf_testlist_show()`. Core helpers prepare requests and media (`mmc_test_prepare_mrq()`, `mmc_test_prepare_sbc()`, `mmc_test_area_init()`), perform blocking/non-blocking transfers (`mmc_test_simple_transfer()`, `mmc_test_nonblock_transfer()`), validate data and expected failures (`mmc_test_transfer()`, `mmc_test_check_result()`, `mmc_test_check_broken_result()`), and save/print performance results.

## Control Flow
The module registers an `mmc_driver` named `mmc_test`. Probe accepts MMC and SD cards but rejects SDUC, registers `test` and `testlist` files under the card debugfs root, and disables eMMC command queue if needed. Writing a number to `test` allocates a `mmc_test_card`, clears previous results for the card, allocates optional highmem pages, claims the host, runs either all cases or the selected case, and releases the host. Each case may run prepare, run, and cleanup callbacks. Results are stored in global lists under `mmc_test_lock` and shown by reading `test`; `testlist` lists numeric case IDs.

## State And Persistence
Runtime state is deliberately transient but can be destructive on the card. The driver writes known data into early sectors for basic validation and into a large middle-card test area for performance tests; cleanup tries to restore the small early area to zero but does not preserve user data in the larger area. Performance metadata persists in memory until the next run, card removal, or module exit. Debugfs dentries are tracked in `mmc_test_file_test`, test results in `mmc_test_result`, and transfer timings in per-test result lists. The pseudo-random generator uses a static `rnd_next`.

## Dependencies And Integration Points
The driver depends on MMC core commands (`mmc_wait_for_req`, `mmc_start_request`, `mmc_pre_req`, `mmc_post_req`, `mmc_erase`, `mmc_set_blocklen`, `mmc_hw_reset`, `mmc_cmdq_disable`, `mmc_cmdq_enable`), card and host capability fields, debugfs, seq_file, user copy helpers, scatterlists, memory allocation, highmem pages, completions, timekeeping, and retuning APIs. It interacts with CMD23 support, command-during-transfer capability, host transfer limits, max segment sizes, erase/trim support, block addressing, CQE/CMDQ state, and host pre/post request callbacks.

## Risks And Edge Cases
The test driver is intentionally unsafe for mounted or valuable media because it writes and erases card regions. Large performance tests can allocate significant memory and run for long periods. Non-blocking tests require both `pre_req` and `post_req` or neither; mismatched host callbacks are rejected. The code has to avoid invalid host/card capabilities, unsupported partial transfers, absent highmem, CMD23 quirks, SDUC addressing, and command queue interference. Debugfs result lists are global, so locking must cover both runs and readers. Failure-path cleanup is important because allocated scatterlists, highmem pages, test-area pages, and debugfs files can otherwise leak.

## Test Signals
The driver is itself a test source. Strong signals are successful debugfs registration, `testlist` exposing all cases, selected case and full-suite runs, expected `UNSUPPORTED` results for missing host/card features, correct data verification for basic writes/reads, expected timeout behavior for broken transfer tests, stable performance result lines, command queue disabled during tests and restored on remove, retuning reliability when supported, reset test recovery, and no leaks or stuck requests after module unload or card removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_test.c -->
