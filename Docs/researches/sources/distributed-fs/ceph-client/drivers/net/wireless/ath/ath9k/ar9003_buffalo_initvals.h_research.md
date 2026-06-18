# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_buffalo_initvals.h

## Purpose
`ar9003_buffalo_initvals.h` provides a board/vendor-specific high-power TX gain table for AR9300/AR9003 hardware used when `ah->config.tx_gain_buffalo` is selected. It overrides the generic AR9300 2.2 high-power TX gain profile without changing the rest of the chip initialization tables.

## Important APIs, Types, And Data
- Include guard: `INITVALS_9003_BUFFALO_H`.
- Exports one table: `ar9300Modes_high_power_tx_gain_table_buffalo[][5]`.
- The table has 102 rows and follows the standard modal TX-gain layout:
  - column 0: register address
  - columns 1-4: `5G_HT20`, `5G_HT40`, `2G_HT40`, `2G_HT20`
- Address coverage starts at `0x0000a2dc` and ends at `0x00016868`, matching the generic high-power table shape.
- The table includes primary TX gain ladder rows around `0x0000a500`-`0x0000a63c`, duplicated chain-specific rows at `0x0000b2dc`/`0x0000c2dc` ranges, and radio/chain calibration values around `0x00016044`, `0x00016444`, and `0x00016844`.

## Control Flow
The header has no executable control flow. Runtime selection happens in `ar9003_tx_gain_table_mode3()` in `ar9003_hw.c`:
- For newer chip revisions, chip-specific high-power tables are selected first.
- In the generic fallback branch, `ah->config.tx_gain_buffalo` selects `ar9300Modes_high_power_tx_gain_table_buffalo`.
- If the flag is not set, the generic `ar9300Modes_high_power_tx_gain_table_2p2` is used instead.

## State And Persistence Behavior
The table is immutable compile-time data. It affects runtime state only when ath9k binds it to `ah->iniModesTxGain` and later writes its entries into device registers during hardware initialization or channel reset. The selection flag is in `struct ath_hw` configuration; this header stores no mutable state.

## Dependencies And Integration Points
- Included by `ar9003_hw.c` alongside the generic AR9003 initvals.
- Depends on the same ath9k modal INI writer assumptions as other `[][5]` TX gain tables.
- Integrated with board configuration through `ah->config.tx_gain_buffalo`, declared in `hw.h`.
- Must remain row-compatible with generic AR9300 high-power TX gain tables so selection can be swapped by pointer without custom programming logic.

## Risks
- Vendor-specific transmit gain values have regulatory and RF-performance implications. Incorrect values may overdrive power, degrade EVM, or violate board limits.
- If row count or register order diverges unexpectedly from the generic high-power table, shared INI programming assumptions may break.
- Because the table is selected by a configuration flag, misdetecting Buffalo hardware can apply this profile to an incompatible board.

## Test Signals
- Build tests should confirm the table compiles and is visible to `ar9003_hw.c`.
- Configuration tests should verify `tx_gain_buffalo` selects this table only in mode 3 fallback paths.
- Hardware validation should measure conducted TX power, EVM, spectral mask, per-rate power limits, and throughput on the target Buffalo boards across 2.4/5 GHz and HT20/HT40.
- Register-dump comparisons against vendor-known init sequences are the strongest regression signal for this file.
