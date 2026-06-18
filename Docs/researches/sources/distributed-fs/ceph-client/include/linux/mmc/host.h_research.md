# sources/distributed-fs/ceph-client/include/linux/mmc/host.h

## Purpose
`mmc/host.h` defines the MMC host-controller contract. It describes bus electrical state, timing, host operations, CQE operations, slot helpers, supplies, host capabilities, runtime state, allocation/registration APIs, regulator helpers, SDIO IRQ handling, retuning helpers, and utility predicates.

## Important APIs, Types, And Functions
Key types are `struct mmc_ios`, `struct mmc_clk_phase`, `struct mmc_clk_phase_map`, `struct sd_uhs2_caps`, `enum sd_uhs2_operation`, `enum mmc_err_stat`, `struct mmc_host_ops`, `struct mmc_cqe_ops`, `struct mmc_slot`, `struct mmc_supply`, `struct mmc_ctx`, and `struct mmc_host`. Capability macros cover bus width, SPI, polling, high-speed, DDR/UHS/HS200/HS400/UHS-II/SD Express/CQE/crypto, card-detect/write-protect polarity, power cycling, and command-during-transfer support. APIs include host allocation/add/remove/free, OF parsing, request completion, CQE completion, regulator setup, SDIO IRQ signaling, PM flag helpers, retune helpers, DMA direction, debug error stats, SD switch/status/tuning/ext-csd helpers, and `mmc_priv()`/`mmc_from_priv()`.

## Control Flow And State
Host drivers allocate a host, fill `ops`, capabilities, voltage/current limits, request limits, optional CQE ops, private data, and register it with `mmc_add_host()`. The core claims the host using `lock`, `wq`, `claimer`, and `claim_cnt`, sets `ios` through `set_ios()`, submits requests through `request()` or `request_atomic()`, completes with `mmc_request_done()`, handles card detection through delayed work and slot state, and manages retuning through flags and `retune_timer`. CQE state (`cqe_enabled`, `cqe_on`, depth, ops) controls queued eMMC requests. Supply state tracks regulators and undervoltage events.

## Dependencies And Integration Points
Dependencies include scheduler, device model, fault injection, debugfs, MMC core/card/PM, DMA direction, block crypto profile, and UHS-II definitions. Integration points include platform/OF parsing, regulators, wakeup sources, PM, SDIO IRQ threads/work, block layer request limits, CQE, inline encryption, debugfs error counters, card detection GPIO helpers, and host-specific tuning/voltage switching callbacks.

## Risks And Test Signals
Risks include incorrect capability advertising, sleeping callbacks used in atomic context, lost request completion, retune races, regulator voltage mismatch, SDIO IRQ wake mishandling, CQE recovery errors, incorrect DMA direction, and card-detect/write-protect polarity bugs. Test signals include host probe/remove, hotplug, suspend/resume, voltage switch, tuning and retuning stress, multiblock I/O, CQE timeout recovery, SDIO IRQ tests, regulator fault/undervoltage tests, and debugfs error counter checks.
