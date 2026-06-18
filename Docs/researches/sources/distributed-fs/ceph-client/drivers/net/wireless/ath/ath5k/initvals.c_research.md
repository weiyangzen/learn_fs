# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/initvals.c

## Purpose
`initvals.c` contains the chip and radio initial register tables used after reset to put ath5k hardware into a clean baseline state. It defines table formats for mode-independent writes and mode-specific writes, then applies AR5210, AR5211, and AR5212-family settings with RF-specific tails and baseband gain tables.

## Important APIs and Control Flow
The two table types are `struct ath5k_ini` for fixed register/value operations and `struct ath5k_ini_mode` for per-mode values indexed by `enum ath5k_driver_mode`. `ath5k_hw_ini_registers()` iterates fixed tables, optionally skips PCU register ranges, supports read-to-clear entries through `AR5K_INI_READ`, throttles writes with `AR5K_REG_WAIT(i)`, and writes defaults. `ath5k_hw_ini_mode_registers()` writes the selected mode value for each mode table row.

`ath5k_hw_write_initvals()` is the public entry point. For AR5212 it writes `ar5212_ini_mode_start`, `ar5212_ini_common_start`, then dispatches by `ah->ah_radio` to RF5111, RF5112, RF5413, RF2316/RF2413, RF2317, or RF2425 tail tables and gain tables, with a few radio-specific overrides. AR5211 writes its mode/common tables and RF5111 baseband gain. AR5210 writes the monolithic AR5210 table.

## State, Dependencies, and Integration
State changes are almost entirely hardware register writes: MAC/QCU/DCU, PCU, timer, PHY, RF, rate-duration, gain, power, and diagnostic registers. The only in-memory inputs are `ah->ah_version`, `ah->ah_radio`, `mode`, and `skip_pcu`. Dependencies are register definitions in `reg.h`, hardware version/radio identifiers in `ath5k.h`, and reset sequencing that calls this before later EEPROM-calibrated PHY and PCU setup.

## Risks and Test Signals
The main risk is that table entries are hardware magic values; small edits can break whole chip families or specific bands. Other risks include wrong mode index, failing to skip PCU registers during partial reset, missing read-to-clear behavior, and RF-specific override drift. Test signals are successful warm reset on each supported MAC/RF combination, stable RX/TX after channel switches, no unsupported channel-mode error except invalid modes, and register dumps matching known vendor/madwifi baselines.
