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
