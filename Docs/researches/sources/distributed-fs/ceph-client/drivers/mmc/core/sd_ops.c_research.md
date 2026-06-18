# sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sd_ops.c

### Purpose
`sd_ops.c` implements low-level SD and SD application command helpers used by card discovery and mode switching. It wraps APP_CMD sequencing, ACMD polling, SCR/SSR reads, SD switch commands, interface-condition checks, RCA retrieval, and SDUC extension-address handling.

### Important APIs, Types, And Functions
Key functions are `mmc_app_cmd()`, `mmc_app_set_bus_width()`, `mmc_send_app_op_cond()`, `mmc_send_ext_addr()`, `mmc_send_if_cond()`, `mmc_send_if_cond_pcie()`, `mmc_send_relative_addr()`, `mmc_app_send_scr()`, `mmc_sd_switch()`, and `mmc_app_sd_status()`. `struct sd_app_op_cond_busy_data` carries ACMD41 polling state for `__mmc_poll_for_busy()`.

### Control Flow
Most application commands first call `mmc_app_cmd()` then submit the real ACMD through `mmc_wait_for_app_cmd()`, which retries by reissuing APP_CMD each attempt. `mmc_send_app_op_cond()` builds ACMD41, polls until busy clears or the 2s timeout expires, and returns the OCR response. `mmc_send_if_cond*()` sends CMD8 and validates the test pattern, with the PCIe variant optionally initializing SD Express and updating `host->ios.timing`. SCR and SSR helpers allocate DMA-safe buffers, issue ADTC reads, convert big-endian SCR words, and return command/data errors. `mmc_sd_switch()` forms CMD6 function-group arguments and reads the 64-byte status buffer.

### State, Persistence, And Dependencies
The helpers mostly do not own state, but they mutate command responses, `host->uhs2_app_cmd` for UHS-II transport, `host->ios.timing` for SD Express probing, and card raw SCR storage. They depend on generic MMC command submission, scatterlists, SD/MMC constants, host/card structures, and `mmc_send_adtc_data()`.

### Integration Points
`sd.c`, `sdio.c`, and `sd_uhs2.c` call these helpers during attach, combo-card setup, bus-width switching, high-speed/UHS negotiation, status reads, and SD-TRAN over UHS-II. `mmc_app_cmd()` contains UHS-II awareness by marking the next packet as APP rather than sending legacy CMD55 directly.

### Risks
APP command retry semantics are subtle because APP_CMD must be resent for every attempt. SPI and native response layouts differ for OCR, R5/R7, and illegal-command checks. CMD8 PCIe probing changes host timing and calls host SD Express init, so failures must preserve legacy SD probing. SCR/SSR callers must pass heap/DMA-safe buffers, as the comments emphasize. UHS-II APP command state must be cleared by packet preparation or subsequent commands can be mislabeled.

### Test Signals
Exercise SDSC/SDHC/SDUC attach, SPI attach, cards that reject CMD8, ACMD41 timeout and retry behavior, APP command illegal-command handling, SCR/SSR DMA reads, CMD6 switch status parsing, SD Express-capable host probing, and UHS-II SD-TRAN APP command packaging.
