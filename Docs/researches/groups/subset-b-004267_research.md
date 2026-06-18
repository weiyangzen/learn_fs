# subset-b-004267 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/mmc.c

## Purpose
`mmc.c` is the eMMC/MMC card attach, enumeration, mode-selection, and power-management implementation for the MMC core. It decodes CID/CSD/EXT_CSD register data into `struct mmc_card`, creates card sysfs attributes, selects bus width/timing/power class, handles cache and command queue enablement, and registers the `struct mmc_bus_ops` used by the core after an MMC device is attached.

## Important APIs, Types, And Functions
The externally visible entry point is `mmc_attach_mmc(struct mmc_host *host)`. Runtime bus callbacks are collected in `mmc_ops`: `.remove`, `.detect`, `.suspend`, `.resume`, `.runtime_suspend`, `.runtime_resume`, `.alive`, `.shutdown`, `.hw_reset`, `.cache_enabled`, `.flush_cache`, and `.handle_undervoltage`. Important internal helpers include `mmc_decode_cid()`, `mmc_decode_csd()`, `mmc_decode_ext_csd()`, `mmc_read_ext_csd()`, `mmc_select_card_type()`, `mmc_select_bus_width()`, `mmc_select_timing()`, `mmc_select_hs()`, `mmc_select_hs200()`, `mmc_select_hs400()`, `mmc_select_hs400es()`, `mmc_hs200_to_hs400()`, `mmc_hs400_to_hs200()`, `_mmc_suspend()`, `_mmc_resume()`, `_mmc_hw_reset()`, `_mmc_flush_cache()`, and `_mmc_handle_undervoltage()`. The local `enum mmc_poweroff_type` distinguishes suspend, shutdown, undervoltage, and unbind power-off paths.

## Control Flow
`mmc_attach_mmc()` puts the host in open-drain mode, probes OCR with CMD1, attaches the MMC bus, selects an acceptable voltage, initializes the card, temporarily releases the host to call `mmc_add_card()`, then reclaims it. `mmc_init_card()` performs the detailed sequence: reset/idle, send operation condition, optional SPI CRC setup, read CID, allocate or validate `oldcard`, set RCA, read and decode CSD/CID, optionally set DSR, select the card, read/decode EXT_CSD, enable erase group definition, reset the user partition, enable power-off notification, choose erase/discard arguments, select timing and bus width, run HS200 tuning and optional HS400 transition, select power class, enable HPI/cache/CMDQ, enable CQE or host software queue, and finally publish `host->card` for new cards. Resume reuses the same path with `oldcard` to reject replacements.

## State And Persistence
Decoded state is persisted in `struct mmc_card`, especially `card->cid`, `card->csd`, `card->ext_csd`, `card->part[]`, partition counts, erase sizing, `erase_arg`, `mmc_avail_type`, `drive_strength`, cache flags, command-queue flags, and suspended/removed markers. Hardware-persistent effects include EXT_CSD writes for ERASE_GROUP_DEF, PART_CONFIG, POWER_OFF_NOTIFICATION, HS_TIMING, BUS_WIDTH, POWER_CLASS, HPI_MGMT, CACHE_CTRL, and CMDQ_MODE_EN. Sysfs attributes expose raw and decoded identifiers, erase/preferred erase/wp group sizes, FFU, lifetime, enhanced/RPMB info, OCR/RCA/DSR, and CMDQ state. Suspend and shutdown may flush the eMMC cache, issue power-off notification or sleep, and power the host off; undervoltage intentionally skips cache flush and marks the card removed.

## Dependencies And Integration Points
The file depends on the MMC core, host, bus, card, SD ops, quirks, and power sequence helpers, plus Linux device, OF, sysfs, PM runtime, randomness, and memory APIs. It calls command helpers from `mmc_ops.c`, host callbacks such as `init_card`, `hs400_downgrade`, `hs400_prepare_ddr`, `prepare_hs400_tuning`, `execute_hs400_tuning`, `hs400_complete`, `hs400_enhanced_strobe`, and CQE callbacks. Block-layer code consumes the resulting card capabilities, partitions, erase parameters, cache behavior, and command queue settings.

## Risks And Edge Cases
EXT_CSD decoding is revision-dependent and very broad; wrong revision gates or bit interpretations can mis-size partitions, enable unsupported modes, or expose stale sysfs data. High-speed transitions are fragile because signal voltage, driver strength, host timing, card timing, tuning, and status polling must be sequenced exactly, with careful fallback for `-EBADMSG`. Card replacement during resume is detected only by CID comparison. Cache flush quirks, power-off notify quirks, HPI quirks, broken manufacturing-date reporting, and host voltage restrictions are all safety-critical. `_mmc_handle_undervoltage()` is fast by design, but skipping cache flush trades completeness for emergency data-integrity handling.

## Test Signals
Useful signals include successful attach on legacy MMC, eMMC 4.x, eMMC 5.0/5.1, SPI MMC, boot/RPMB/GP partition exposure, sysfs attribute sanity, erase/discard/trim behavior, HPI/BKOPS/cache/CMDQ enablement, HS/DDR/HS200/HS400/HS400ES negotiation, retuning, runtime suspend/resume, shutdown power-off notification, hardware reset recovery, card replacement detection on resume, CQE enablement, and injected undervoltage events that lead to a graceful short power-off path and removed-card state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.c

## Purpose
`mmc_ops.c` contains low-level MMC command helpers shared by card enumeration, block operations, tuning, maintenance, and drivers that need direct MMC command transactions. It wraps command construction, request setup, busy polling, EXT_CSD switching, tuning-pattern validation, bus-width testing, background operations, command queue toggling, sanitize, and read-tuning probes.

## Important APIs, Types, And Functions
Exported helpers include `__mmc_send_status()`, `mmc_send_status()`, `mmc_get_ext_csd()`, `__mmc_poll_for_busy()`, `mmc_poll_for_busy()`, `mmc_prepare_busy_cmd()`, `__mmc_switch()`, `mmc_switch()`, `mmc_send_tuning()`, `mmc_send_abort_tuning()`, `mmc_run_bkops()`, `mmc_cmdq_enable()`, `mmc_cmdq_disable()`, `mmc_sanitize()`, and `mmc_read_tuning()`. Internal helpers include `_mmc_select_card()`, `mmc_send_cxd_native()`, `mmc_spi_send_cxd()`, `mmc_send_bus_test()`, `mmc_interrupt_hpi()`, and the busy callbacks. `struct mmc_busy_data` and `struct mmc_op_cond_busy_data` carry polling context, while `enum mmc_busy_cmd` is declared in the header.

## Control Flow
Simple helpers build `struct mmc_command` and call `mmc_wait_for_cmd()`. Data-transfer helpers build `struct mmc_request`, `struct mmc_command`, `struct mmc_data`, and a scatterlist, then call `mmc_wait_for_req()`. `mmc_send_op_cond()` repeatedly issues CMD1 through `__mmc_poll_for_busy()` until the card leaves busy or the timeout expires. `__mmc_switch()` holds retuning, prepares CMD6 with R1/R1B according to host busy-timeout limits, sends it, optionally polls busy with CMD13 or `card_busy()`, switches host timing if requested, checks switch status, and restores timing on failure. Tuning reads a standard 4-bit or 8-bit pattern and compares it byte-for-byte.

## State And Persistence
Most helpers are stateless wrappers, but several update host/card state. `mmc_spi_set_crc()` updates `host->use_spi_crc`, `mmc_cmdq_switch()` updates `card->ext_csd.cmdq_en`, `mmc_read_bkops_status()` refreshes BKOPS and exception status fields, and `mmc_get_ext_csd()` returns a newly allocated 512-byte EXT_CSD copy to the caller. EXT_CSD switch helpers persistently modify card registers such as timing, bus width, cache, command queue, sanitize start, and BKOPS start. HPI and sanitize paths may attempt to abort a long-running program state.

## Dependencies And Integration Points
This file is central to `mmc.c`, block erase/maintenance paths, tuning code, test code, and external MMC drivers using exported GPL helpers. It depends on host capabilities such as SPI/native bus mode, `MMC_CAP_WAIT_WHILE_BUSY`, `MMC_CAP_NEED_RSP_BUSY`, `max_busy_timeout`, `card_busy`, CMD23 capability, and retuning controls. It integrates with request-layer APIs, scatterlists, endian conversion for SPI CID/CSD reads, JEDEC command constants, and block-layer maintenance operations through sanitize/BKOPS/CMDQ support.

## Risks And Edge Cases
Busy handling is subtle: hosts with insufficient `max_busy_timeout` are forced from R1B to R1 plus software polling, and callers that disallow CMD13 polling may fall back to sleeping for the declared timeout. CRC errors are sometimes fatal and sometimes tolerated, depending on timing transitions and caller intent. `mmc_switch_status()` must account for native versus SPI status format. Tuning depends on correct bus width and exact patterns. HPI abort is legal only in the PRG state and only when enabled. `mmc_read_tuning()` deliberately discards read data and uses fixed timeout semantics, so it is a probe rather than a data validation helper.

## Test Signals
Validation should cover native and SPI command paths, CMD1 polling timeout, CID/CSD reads, EXT_CSD allocation/error cleanup, CMD6 with hardware busy, software busy, card-busy callback, and no-poll sleep fallback. Mode-switch tests should exercise CRC-error-tolerant HS200/HS400 transitions. Tuning tests should cover 4-bit and 8-bit patterns and abort tuning. Maintenance tests should cover BKOPS levels, HPI abort on timeout, CMDQ enable/disable, sanitize default and custom timeouts, and `mmc_read_tuning()` single and multi-block reads with and without CMD23.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h

## Purpose
`mmc_ops.h` declares the low-level MMC command helper interface used inside the MMC core and by a few GPL-exported consumers. It is the contract between enumeration, block, tuning, maintenance, and test code and the command implementation in `mmc_ops.c`.

## Important APIs, Types, And Functions
The header defines `enum mmc_busy_cmd` with busy contexts for CMD6 switch, erase, HPI, reliable single operations, and generic I/O. It forward-declares `struct mmc_host`, `struct mmc_card`, and `struct mmc_command`, then declares helpers for card select/deselect, DSR, GO_IDLE, OP_COND, RCA, ADTC data, CSD/CID/EXT_CSD/OCR/SPI CRC, bus tests, switch status, busy command preparation/polling, EXT_CSD switching, BKOPS, CMDQ, sanitize, and the inline `unstuff_bits()`.

## Control Flow
This file has no runtime flow except `unstuff_bits()`, which extracts a bitfield from a 128-bit big-endian-style MMC response array. Callers pass response words, start bit, and size; the helper computes the response word offset, shifts the selected bits, pulls from the previous word when the field crosses a 32-bit boundary, and masks the final value.

## State And Persistence
The header owns no persistent state. Its declarations enable command helpers that mutate host/card/hardware state in other files. The inline bit extraction is deterministic and only reads the provided response buffer.

## Dependencies And Integration Points
`mmc.c`, `mmc_test.c`, block code, SD operation helpers, and host logic include this header to avoid duplicating command construction. The `unstuff_bits()` inline is especially important for CID and CSD decoding in `mmc.c`. The busy command enum is interpreted by `mmc_poll_for_busy()` in `mmc_ops.c`.

## Risks And Edge Cases
The `unstuff_bits()` helper assumes valid field sizes and valid response layout; misuse with a zero or oversized range, wrong start bit, or a short response buffer would silently decode bad card metadata. Header/API drift between declarations and exported symbols would break consumers. The busy enum must stay synchronized with `mmc_busy_cb()` switch handling.

## Test Signals
Compile coverage across MMC core users is the primary signal. Functional signals include correct CID/CSD decoding through `unstuff_bits()`, successful calls to all declared helpers from enumeration and block paths, and no missing-prototype or enum-handling warnings when adding new busy command types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c

## Purpose
`pwrseq.c` implements the common MMC power-sequence registry and dispatch layer. It lets platform power-sequence providers register `struct mmc_pwrseq` objects and lets MMC hosts bind to one through an `mmc-pwrseq` device-tree phandle.

## Important APIs, Types, And Functions
The exported registration API is `mmc_pwrseq_register()` and `mmc_pwrseq_unregister()`. Host-facing helpers are `mmc_pwrseq_alloc()`, `mmc_pwrseq_pre_power_on()`, `mmc_pwrseq_post_power_on()`, `mmc_pwrseq_power_off()`, `mmc_pwrseq_reset()`, and `mmc_pwrseq_free()`. Internal state is the global `pwrseq_list` protected by `pwrseq_list_mutex`.

## Control Flow
During host setup, `mmc_pwrseq_alloc()` reads the `mmc-pwrseq` phandle from the host parent's OF node, scans the registered provider list for a matching provider device node, takes the provider module reference with `try_module_get()`, and stores the provider in `host->pwrseq`. If the phandle exists but no provider has registered, it returns `-EPROBE_DEFER`. Later MMC power transitions call the dispatcher helpers, which invoke only the implemented callbacks in `pwrseq->ops`.

## State And Persistence
The file persists provider registrations in a global list and stores the selected provider pointer in `host->pwrseq`. It also owns module reference lifetime for the bound provider and drops it in `mmc_pwrseq_free()`. Hardware state changes are delegated to provider modules; this file only dispatches callbacks.

## Dependencies And Integration Points
It depends on device tree phandles, Linux module reference counting, device-node matching, MMC host state, and provider implementations in files such as `pwrseq_simple.c`, `pwrseq_emmc.c`, and `pwrseq_sd8787.c`. Core power paths call the pre/post/off/reset dispatchers around host power changes and hardware reset fallback.

## Risks And Edge Cases
Provider probe ordering can legitimately produce `-EPROBE_DEFER`. A provider with missing `ops` or `dev` is rejected at registration, but individual callbacks are optional. `try_module_get()` failure leaves the host without a pwrseq and logs an error. Unregistering a provider while a host still holds a module reference should be prevented by module lifetime, but stale device-tree references or missing providers block host probe.

## Test Signals
Validation includes hosts with no `mmc-pwrseq` phandle returning success, hosts with a phandle deferring until the provider loads, provider register/unregister operations, module reference balancing, and visible invocation of pre-power-on, post-power-on, power-off, and reset callbacks during host power transitions and hardware reset fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h

## Purpose
`pwrseq.h` defines the internal MMC power-sequence provider contract. It gives provider drivers a common `struct mmc_pwrseq` shape and gives host/core code a stable set of lifecycle helpers.

## Important APIs, Types, And Functions
`struct mmc_pwrseq_ops` contains optional `pre_power_on`, `post_power_on`, `power_off`, and `reset` callbacks. `struct mmc_pwrseq` stores the ops pointer, backing `struct device`, global list node, and owning module. Under `CONFIG_OF`, the header declares provider registration, allocation, dispatch, reset, and free helpers. Without `CONFIG_OF`, registration returns `-ENOSYS`, allocation returns success, and dispatch/free helpers compile to no-ops.

## Control Flow
The header has no active runtime control flow beyond the non-OF inline stubs. The intended flow is provider probe fills `struct mmc_pwrseq` and registers it, host allocation binds by phandle, and the MMC core dispatches callbacks during power transitions.

## State And Persistence
The data structures define persistent in-kernel state: provider identity, callback table, list membership, and module ownership. In non-OF builds, no power-sequence state is persisted because helpers are disabled/stubbed.

## Dependencies And Integration Points
The header depends on Linux list/module/device types through users and on `struct mmc_host`. It is included by the common registry and provider modules. Host code observes only the helper API and does not need to know which provider implements a sequence.

## Risks And Edge Cases
Power sequencing is OF-gated. Non-OF platforms that need special sequencing cannot use this path without additional code. Providers must keep `ops`, `dev`, and `owner` valid for as long as they are registered, and callers must tolerate missing callbacks. Adding a new callback requires coordinated updates to the header, registry dispatchers, and providers.

## Test Signals
Compile tests with and without `CONFIG_OF` verify the stubs and declarations. Runtime tests should show provider binding and callback dispatch only on OF-enabled platforms with a matching `mmc-pwrseq` phandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c

## Purpose
`pwrseq_emmc.c` is a power-sequence provider for eMMC reset lines. It exposes the `mmc-pwrseq-emmc` compatible and implements hardware reset by toggling a `reset` GPIO.

## Important APIs, Types, And Functions
The provider-private `struct mmc_pwrseq_emmc` embeds `struct mmc_pwrseq`, a `notifier_block` for restart handling, and `reset_gpio`. `mmc_pwrseq_emmc_reset()` is the MMC reset callback. `mmc_pwrseq_emmc_reset_nb()` is a restart handler for emergency reboot when the GPIO can be toggled without sleeping. Probe and remove are handled by `mmc_pwrseq_emmc_probe()` and `mmc_pwrseq_emmc_remove()`.

## Control Flow
Probe allocates provider state, obtains the `reset` GPIO as output-low, optionally registers a high-priority restart handler if the GPIO is non-sleeping, fills `pwrseq.ops/dev/owner`, stores driver data, and registers with `mmc_pwrseq_register()`. Reset asserts the GPIO, waits 1 microsecond, deasserts it, and waits 200 microseconds. Remove unregisters the restart handler and the pwrseq provider.

## State And Persistence
Runtime state is devm-managed provider memory, the reset GPIO descriptor, registered pwrseq list entry, and optional restart handler. Hardware-visible state is the reset GPIO level. The emergency reboot handler exists so the eMMC can be reset even during urgent restart paths where normal sleepable GPIO access is unavailable.

## Dependencies And Integration Points
The file depends on platform-driver binding, OF compatible matching, GPIO consumer APIs, restart handlers, delays, MMC host/pwrseq APIs, and module infrastructure. It integrates with `pwrseq.c` through provider registration and with MMC hardware reset fallback through `.reset`.

## Risks And Edge Cases
If the reset GPIO is sleep-capable, emergency-reboot reset is disabled and a notice is logged. Remove unconditionally calls `unregister_restart_handler()` even when the handler was not registered, relying on notifier semantics to tolerate it. Incorrect GPIO polarity in device tree would invert reset behavior. The timing constants are minimal and may not be enough for all boards if hardware needs a longer reset pulse.

## Test Signals
Tests should verify probe defers or fails cleanly when the GPIO is missing/not ready, host phandle binding succeeds, `mmc_hw_reset()` toggles the GPIO, emergency restart toggles only for non-sleeping GPIOs, and provider unregister removes the pwrseq entry without leaving stale host references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_emmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_sd8787.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_sd8787.c

## Purpose
`pwrseq_sd8787.c` provides board-level power sequencing for SDIO Wi-Fi/Bluetooth chips that need reset and powerdown GPIO sequencing before the MMC/SDIO host powers up. It supports Marvell SD8787 and Microchip/Atmel WILC1000 compatible strings with different GPIO ordering and delays.

## Important APIs, Types, And Functions
Provider state is `struct mmc_pwrseq_sd8787`, embedding `struct mmc_pwrseq` plus `reset_gpio` and `pwrdn_gpio`. SD8787 callbacks are `mmc_pwrseq_sd8787_pre_power_on()` and `mmc_pwrseq_sd8787_power_off()`. WILC1000 callbacks are `mmc_pwrseq_wilc1000_pre_power_on()` and `mmc_pwrseq_wilc1000_power_off()`. Probe uses `mmc_pwrseq_sd8787_of_match[]` to select the correct callback table.

## Control Flow
Probe allocates state, matches the OF node, obtains `powerdown` and `reset` GPIOs as output-low, attaches the matched ops table, and registers the provider. SD8787 pre-power-on asserts reset, sleeps 300 ms, then enables powerdown. SD8787 power-off disables powerdown and reset. WILC1000 pre-power-on asserts chip enable, waits 5 ms, then releases reset; power-off drops reset then chip enable. Remove unregisters the provider.

## State And Persistence
Persistent kernel state is the registered provider and the two GPIO descriptors. Hardware state is the level of powerdown/chip-enable and reset pins. No state is stored in the host beyond `host->pwrseq` after binding.

## Dependencies And Integration Points
The module depends on OF platform matching, GPIO consumer APIs, sleepable delays, MMC host/pwrseq APIs, and provider registration. It integrates with SDIO card discovery because its pre-power-on callback must prepare the chip before the host enumerates it.

## Risks And Edge Cases
The same struct and GPIO names serve two chips whose pin meanings differ; incorrect compatible strings or device-tree polarity can leave devices held in reset or powered down. `of_match_node()` is assumed to return a valid match for a probed device. Fixed sleeps may be insufficient or excessive for some board designs. Missing GPIOs fail probe and therefore defer or block host pwrseq binding.

## Test Signals
Board tests should verify GPIO order and timing on SD8787 and WILC1000, successful `mmc-pwrseq` phandle allocation by an SDIO host, device enumeration after pre-power-on, clean GPIO deassertion on power-off, and provider unregister on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_sd8787.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c

## Purpose
`pwrseq_simple.c` implements the generic `mmc-pwrseq-simple` provider for boards that need an external clock and reset GPIOs or reset controller sequencing around MMC power on/off.

## Important APIs, Types, And Functions
Provider state is `struct mmc_pwrseq_simple`, which embeds `struct mmc_pwrseq` and stores `clk_enabled`, post-power-on and power-off delays, optional `ext_clk`, optional reset GPIO array, and optional reset controller. Main callbacks are `mmc_pwrseq_simple_pre_power_on()`, `mmc_pwrseq_simple_post_power_on()`, and `mmc_pwrseq_simple_power_off()`. `mmc_pwrseq_simple_set_gpios_value()` sets all reset GPIOs together using a bitmap.

## Control Flow
Probe allocates state, gets optional `ext_clock`, optionally chooses a shared reset controller when exactly one reset GPIO phandle is present, otherwise falls back to a `reset` GPIO array, reads delay properties, fills the pwrseq fields, and registers the provider. Pre-power-on enables the external clock if present and asserts reset through either reset control or GPIOs. Post-power-on releases reset and waits the configured post-power-on delay. Power-off asserts reset, waits the configured power-off delay, and disables the external clock if it had been enabled.

## State And Persistence
The provider tracks whether the external clock is currently enabled to balance prepare/enable and disable/unprepare calls. It also holds reset descriptors and delay settings for the provider lifetime. Hardware-visible state consists of reset-line assertion/deassertion and external clock state.

## Dependencies And Integration Points
The file depends on platform/OF matching, clock framework, GPIO consumer arrays, bitmap allocation, reset controller APIs, device properties, sleep delays, and the pwrseq registry. It integrates with any MMC host whose device tree references an `mmc-pwrseq-simple` node.

## Risks And Edge Cases
Bitmap allocation failure in GPIO setting silently leaves reset GPIOs unchanged for that callback. Reset-controller use is selected only for a single reset GPIO phandle; multiple reset lines fall back to GPIO control. Optional clock/reset resources may be absent, but real hardware may still require them. Incorrect reset polarity or delay properties can break enumeration. Clock enable errors are not checked in the callback, so a failed clock preparation could leave later enumeration failures as the only symptom.

## Test Signals
Validation should cover providers with only GPIO reset, only reset controller, external clock plus reset, missing optional resources, configured delays, repeated power cycles with balanced clock state, and host enumeration through a matching `mmc-pwrseq-simple` phandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c

## Purpose
`queue.c` bridges MMC block requests to the Linux blk-mq layer. It creates request queues and gendisks, classifies requests for synchronous, direct-command, and asynchronous issue, maps scatterlists, dispatches requests to `mmc_blk_mq_issue_rq()`, handles CQE/HSQ recovery and timeouts, and manages queue suspend/resume/cleanup.

## Important APIs, Types, And Functions
Public functions are `mmc_init_queue()`, `mmc_cleanup_queue()`, `mmc_queue_suspend()`, `mmc_queue_resume()`, `mmc_queue_map_sg()`, `mmc_cqe_check_busy()`, `mmc_cqe_recovery_notifier()`, and `mmc_issue_type()`. Important internals include `mmc_mq_queue_rq()`, `mmc_mq_timed_out()`, `mmc_cqe_timed_out()`, `mmc_mq_recovery_handler()`, `mmc_mq_init_request()`, `mmc_mq_exit_request()`, `mmc_alloc_disk()`, `mmc_queue_setup_discard()`, and `mmc_get_max_segments()`. `mmc_mq_ops` is the blk-mq operation table.

## Control Flow
`mmc_init_queue()` initializes queue state, configures a blk-mq tag set, detects DMA merge capability, allocates tags, then calls `mmc_alloc_disk()` to build queue limits and allocate the disk. `mmc_mq_queue_rq()` rejects removed cards, classifies the request, checks recovery/busy state, applies CQE DCMD and HSQ-depth throttling, marks the queue busy, increments in-flight counts, gets the card for the first outstanding request, starts the blk request, and calls `mmc_blk_mq_issue_rq()`. Failed starts decrement in-flight counts and may put the card. CQE timeouts delegate to host CQE timeout handling and schedule recovery when requested. Recovery work claims the card context, invokes CQE or normal recovery, clears recovery state, finishes HSQ recovery if needed, releases the card, and reruns hardware queues.

## State And Persistence
`struct mmc_queue` stores card pointer, context, tag set, request queue, lock, in-flight counters per issue type, CQE busy flags, busy/recovery/in_recovery booleans, work items, waits, completion fields, and block data pointer. Per-request private data stores the MMC request, commands, data, scatterlist pointer, driver-operation metadata, retries, and flags. Queue limits persist in the block queue: discard/secure erase/write zeroes limits, logical block size, max hardware sectors, max segments, max segment size or virt boundary, timeout, and crypto configuration.

## Dependencies And Integration Points
The file integrates Linux blk-mq, request queues, gendisks, DMA merge boundaries, scatterlists, workqueues, MMC block implementation (`mmc_blk_mq_issue_rq`, completion, recovery), CQE host operations, crypto queue setup, erase/discard capability helpers, and host/card capability fields. The block driver consumes the initialized gendisk and queue, while host drivers affect queue depth, merging, timeouts, and CQE behavior.

## Risks And Edge Cases
Concurrency is guarded by spinlocks, busy flags, workqueues, and in-flight counters; mistakes can stall requests, over-release the card, or run recovery while new work is dispatched. CQE direct commands are limited to one in flight. Synchronous requests get large timeouts because the core cannot abort them through a host API. Queue limits must match host DMA and card capabilities or data corruption/performance regressions can result. Cleanup must cancel recovery and flush completion work after freeing tags to avoid use-after-free. The file contains a trailing whitespace line near `mq->card = card`, but it is harmless behaviorally.

## Test Signals
Signals include successful block device creation, correct queue depths for CQE and non-CQE hosts, discard/secure erase/write zeroes limits, logical block size 512/4096 handling, DMA merge behavior, stable read/write/flush/discard/ioctl dispatch, CQE DCMD throttling, timeout-triggered CQE recovery, HSQ recovery finish, suspend quiescing with no outstanding requests, resume unquiescing, and cleanup under card removal during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h

## Purpose
`queue.h` defines the MMC block queue data structures and helper prototypes shared between `queue.c` and the MMC block implementation. It is the typed contract for blk-mq private request state, queue state, driver operations, and issue classification.

## Important APIs, Types, And Functions
The header defines `enum mmc_issued`, `enum mmc_issue_type`, `enum mmc_drv_op`, `struct mmc_blk_request`, `struct mmc_queue_req`, and `struct mmc_queue`. Inline helpers convert between `struct request` and `struct mmc_queue_req`, compute total in-flight request count with `mmc_tot_in_flight()`, and compute CQE queue count with `mmc_cqe_qcnt()`. It declares queue lifecycle, scatterlist mapping, CQE busy/recovery notification, and issue-type classification functions.

## Control Flow
The header itself has only inline conversion and counter helpers. Runtime control flow is implemented by `queue.c` and block code using the structures declared here: blk-mq allocates request PDUs as `struct mmc_queue_req`, block code fills the embedded `struct mmc_blk_request`, and queue code dispatches according to `enum mmc_issue_type`.

## State And Persistence
The persistent queue state includes card/context/tag-set pointers, block queue pointer, in-flight counts, CQE busy flags, recovery state, waiting/completion state, and work items. Per-request state includes command/request data, scatterlist pointer, driver operation type and result, ioctl metadata, retry count, and flags such as `MQRQ_XFER_SINGLE_BLOCK`.

## Dependencies And Integration Points
It depends on Linux block, blk-mq, MMC core, and MMC host headers. It is consumed by `queue.c`, `block.c`, CQE completion/recovery paths, and ioctl/RPMB/boot write-protect paths. The issue-type enum aligns with the in-flight counter array and queue/CQE scheduling policy.

## Risks And Edge Cases
The `in_flight` array size and `enum mmc_issue_type` values must remain synchronized. Request/private-data conversion assumes blk-mq `cmd_size` is set to `sizeof(struct mmc_queue_req)`. New driver operations must update all switch statements in block and queue code. Incorrect use of the inline counters can affect card lifetime management and CQE retuning decisions.

## Test Signals
Compile coverage across queue/block code is critical. Runtime signals include correct request PDU allocation, ioctl and RPMB operations using the expected `drv_op`, in-flight counters returning to zero after requests, CQE queue counts matching dispatched DCMD/async requests, and no type or structure mismatch under blk-mq debug options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h

## Purpose
`quirks.h` defines card-specific SD, MMC, eMMC EXT_CSD, and SDIO fixup tables plus the matcher that applies them to `struct mmc_card`. It centralizes known hardware and firmware workarounds for broken cache flush, power-off notification, tuning, discard, CMD23, read timeout, secure erase/trim, HPI, metadata reporting, SDIO byte mode, interrupt polling, and rate limits.

## Important APIs, Types, And Functions
Important data tables are `mmc_sd_fixups[]`, `mmc_blk_fixups[]`, `mmc_ext_csd_fixups[]`, `sdio_fixup_methods[]`, and `sdio_card_init_methods[]`. Helper functions are `mmc_fixup_of_compatible_match()` and `mmc_fixup_device()`. The tables use macros such as `MMC_FIXUP`, `_FIXUP_EXT`, `MMC_FIXUP_EXT_CSD_REV`, `SDIO_FIXUP`, and `SDIO_FIXUP_COMPATIBLE`, and call vendor fixup functions like `add_quirk`, `add_quirk_sd`, `add_quirk_mmc`, `add_limit_rate_quirk`, and `wl1251_quirk`.

## Control Flow
Callers pass a card and one of the fixup tables to `mmc_fixup_device()`. The function computes the card revision, iterates until `END_FIXUP`, and checks manufacturer, OEM, product name, SDIO CIS vendor/device, EXT_CSD revision, revision range, optional OF compatible child match, year, and month. Matching entries log the callback symbol and call the stored vendor fixup with the table data. OF-compatible matching scans child nodes under the host device node.

## State And Persistence
The tables are static read-only policy. Persistent effects are changes made by vendor fixup callbacks to `struct mmc_card`, such as setting quirk bits or limiting rates. These quirk bits later influence discard/trim, cache flush, CMD23 use, tuning, HPI enablement, SDIO behavior, and block-layer limits.

## Dependencies And Integration Points
The file depends on OF helpers, SDIO IDs, local card/fixup definitions, CID fields, CIS fields, EXT_CSD revision, and card quirk callbacks. It is included by core/card initialization code rather than compiled as an independent translation unit. `mmc.c` explicitly applies `mmc_ext_csd_fixups[]` after decoding the EXT_CSD revision, and other MMC/SD/SDIO paths use the other tables during card setup.

## Risks And Edge Cases
The tables encode real hardware errata, so overly broad matches can disable useful features or reduce performance on unaffected cards, while too-narrow matches leave data-corruption bugs active. Manufacturing-date and revision matching must handle vendor reporting errors. Product-name comparisons use fixed-size CID product names. OF-compatible quirks depend on board descriptions. Adding new quirks requires choosing the right table so required fields, especially EXT_CSD revision, are available at application time.

## Test Signals
Signals include matching known affected cards, non-matching adjacent card revisions/dates, expected quirk bits in debug output, changed block limits for broken discard/trim/cache/CMD23 cases, disabled HPI for affected eMMC revisions, SDIO quirks applied by vendor/device or compatible string, and no regressions on unaffected cards from the same manufacturer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c

## Purpose
`regulator.c` provides MMC host helper functions for VMMC, VQMMC, and VQMMC2 regulator discovery and voltage control. It also wires regulator undervoltage events into the MMC core's emergency undervoltage handling path.

## Important APIs, Types, And Functions
Exported helpers include `mmc_regulator_set_ocr()`, `mmc_regulator_set_vqmmc()`, `mmc_regulator_set_vqmmc2()`, `mmc_regulator_get_supply()`, `mmc_regulator_enable_vqmmc()`, and `mmc_regulator_disable_vqmmc()`. Undervoltage helpers are `mmc_undervoltage_workfn()`, `mmc_regulator_register_undervoltage_notifier()`, `mmc_regulator_unregister_undervoltage_notifier()`, and internal `mmc_handle_regulator_event()`. Voltage conversion helpers include `mmc_ocrbitnum_to_vdd()`, `mmc_regulator_get_ocrmask()`, and `mmc_regulator_set_voltage_if_supported()`.

## Control Flow
`mmc_regulator_get_supply()` obtains optional `vmmc`, `vqmmc`, and `vqmmc2` regulators, returns probe defer for unavailable required-at-probe providers, and derives `mmc->ocr_avail` from `vmmc` voltages when possible. `mmc_regulator_set_ocr()` converts a host OCR bit to a voltage range, sets and enables VMMC, or disables it when `vdd_bit` is zero while tracking `mmc->regulator_enabled`. `mmc_regulator_set_vqmmc()` switches signaling voltage for 1.2 V, 1.8 V, or 3.3 V, trying to keep 3.3 V signaling close to VMMC before falling back to the full 2.7-3.6 V range. VQMMC2 currently supports 1.8 V. Undervoltage notifier registration attaches a regulator notifier to VMMC; an under-voltage event sets `host->undervoltage` under lock and queues high-priority work that calls `mmc_handle_undervoltage(host)`.

## State And Persistence
The file updates `mmc->supply` regulator pointers, `mmc->ocr_avail`, `mmc->regulator_enabled`, `mmc->vqmmc_enabled`, `host->undervoltage`, notifier block fields, and delayed/high-priority work state. Hardware-visible persistent state includes regulator enablement and selected voltage levels. Unregister cancels pending undervoltage work after unregistering the notifier.

## Dependencies And Integration Points
It depends on `CONFIG_REGULATOR` for OCR mask derivation and voltage setting, Linux regulator consumer APIs, workqueues, host locking, MMC OCR conversion, and core `mmc_handle_undervoltage()`. Host controller drivers call these helpers from probe and `set_ios()` or voltage-switch callbacks. `mmc.c` provides the bus-level undervoltage handler that can power off and remove a card.

## Risks And Edge Cases
Optional regulators are represented by error pointers and must be checked by callers that require them. `mmc_regulator_set_ocr()` calls the voltage converter without checking its return value, so invalid OCR bits rely on downstream regulator errors. Voltage switching returns a positive value when no change was needed, which callers must not treat as failure. Under-voltage event coalescing depends on `host->undervoltage` and high-priority work; if never cleared by higher layers, later events are ignored. Emergency undervoltage handling can remove the card, so user-visible I/O failures are expected after the event.

## Test Signals
Validation should cover hosts with no regulators, probe deferral, OCR mask derivation from listed and fixed voltages, VMMC enable/disable balancing, VQMMC 1.2/1.8/3.3 V switches including no-change positive returns, VQMMC2 1.8 V, regulator error logging, undervoltage notifier registration/unregistration, event coalescing, cancellation on unregister, and the full path from regulator under-voltage event to MMC card power-off/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/regulator.c -->
