# sources/distributed-fs/ceph-client/include/linux/mmc/core.h

## Purpose
`mmc/core.h` defines the request, command, data, and UHS-II command objects passed between MMC core, block layer, card logic, and host drivers. It also declares synchronous request/command helpers and reset/timeout helpers.

## Important APIs, Types, And Functions
Important types are `struct uhs2_command`, `struct mmc_command`, `struct mmc_data`, and `struct mmc_request`. Macros describe native and SPI response bits, response presets (`MMC_RSP_R1`, `MMC_RSP_R1B`, `MMC_RSP_R2`, etc.), command classes (`MMC_CMD_AC`, `MMC_CMD_ADTC`, `MMC_CMD_BC`, `MMC_CMD_BCR`), data flags (`MMC_DATA_WRITE`, `MMC_DATA_READ`, CQE flags), and helpers `mmc_resp_type()`, `mmc_spi_resp_type()`, and `mmc_cmd_type()`. Declared functions include `mmc_wait_for_req()`, `mmc_wait_for_cmd()`, `mmc_hw_reset()`, `mmc_sw_reset()`, and `mmc_set_data_timeout()`.

## Control Flow And State
The normal flow is: fill a `mmc_command`, optional `mmc_data`, optional SET_BLOCK_COUNT/STOP commands, and a `mmc_request`; submit to the host; complete via the request completions or `done()` callback; inspect `cmd->error`, `data->error`, `bytes_xfered`, and optional recovery notifier. UHS-II native packet data can be attached through `uhs2_command`. State is per-request and transient, with optional crypto context and key slot when MMC crypto is enabled.

## Dependencies And Integration Points
Dependencies include completions, scatterlists via forward declarations, MMC host/card structures, optional inline crypto, and UHS-II support. Integration points include host `request()`/CQE operations, MMC block requests, SD/MMC command encoding headers, error recovery, tuning, reset handling, and data timeout computation.

## Risks And Test Signals
Risks include response flag mismatch, SPI/native response confusion, incorrect busy timeout, invalid scatter-gather counts, completion ordering bugs, CQE recovery omissions, and crypto context lifetime issues. Test signals include command encode/decode tests, host simulator tests, block read/write/multiblock I/O, timeout/retry injection, CQE recovery tests, UHS-II command responses, and crypto-enabled builds.
