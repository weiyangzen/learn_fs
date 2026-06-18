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
