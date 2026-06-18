# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_2p2_initvals.h

## Purpose
`ar9003_2p2_initvals.h` is a static hardware initialization data header for the ath9k AR9003 2.2 family. It contains register/value tables consumed by the AR9003 hardware setup path to program MAC, baseband, radio, SoC, PCIe SERDES, fast-clock, CCK Japan 2484 MHz, DFS, RX gain, and multiple TX gain profiles.

The file has no executable code. Its behavior is entirely in the shape and values of `static const u32` INI arrays. `ar9003_hw.c` includes the header and registers these arrays with `INIT_INI_ARRAY()` for the fallback AR9300/AR9003 2.2 path and as shared tables for later chips that `#define` their own names to these arrays.

## Important APIs, Types, And Data
- Include guard: `INITVALS_9003_2P2_H`.
- Table row conventions:
  - `[][2]`: address plus one value, usually non-modal core/preamble tables.
  - `[][3]`: address plus two modal values, used for fast-clock/DFS variants.
  - `[][5]`: address plus `5G_HT20`, `5G_HT40`, `2G_HT40`, `2G_HT20` values.
- Key tables and coverage:
  - `ar9300_2p2_radio_postamble` has 9 rows over radio-chain addresses `0x0001609c` through `0x00016940`.
  - `ar9300_2p2_radio_core` has 140 rows over radio core addresses `0x00016000` through `0x00016bd4`.
  - `ar9300_2p2_mac_core` has 153 rows over MAC addresses `0x00000008` through `0x000083d0`.
  - `ar9300_2p2_mac_postamble` has 8 modal rows.
  - `ar9300_2p2_soc_preamble` has 6 rows and `ar9300_2p2_soc_postamble` has 1 row.
  - `ar9300_2p2_baseband_core` has 159 rows and `ar9300_2p2_baseband_postamble` has 52 modal rows.
  - `ar9300Common_rx_gain_table_2p2` and `ar9300Common_wo_xlna_rx_gain_table_2p2` each have 256 RX gain rows.
  - TX gain profiles include `lowest_ob_db`, `low_ob_db`, `high_ob_db`, `high_power`, `mixed_ob_db`, and `type5`. Most have 102 modal rows; `type5` has 70 rows.
  - Special-purpose tables are `ar9300Modes_fast_clock_2p2`, `ar9300PciePhy_pll_on_clkreq_disable_L1_2p2`, `ar9300_2p2_baseband_core_txfir_coeff_japan_2484`, and `ar9300_2p2_baseband_postamble_dfs_channel`.

## Control Flow
The header itself has no branches or functions. Runtime control flow lives in `ar9003_hw_init_mode_regs()` and TX-gain mode selectors in `ar9003_hw.c`:
- For the generic AR9300/AR9003 2.2 branch, `iniMac`, `iniBB`, `iniRadio`, `iniSOC`, `iniModesRxGain`, `iniModesTxGain`, `iniPcieSerdes`, `iniPcieSerdesLowPower`, `iniModesFastClock`, `iniCckfirJapan2484`, and `ini_dfs` are bound to this file's arrays.
- `ar9003_tx_gain_table_mode0()` through mode 5 select the appropriate TX gain table. Fallback cases use this file's AR9300 2.2 tables when no newer chip-specific override is selected.
- Other initval headers alias selected shared tables, especially Japan CCK FIR and DFS/SoC postamble data, through preprocessor `#define`s.

## State And Persistence Behavior
The arrays are compile-time constant data stored in the kernel image. They do not persist state, allocate memory, or mutate. Their values become device state only when the ath9k register programming code writes them to hardware registers during reset/channel setup. Any persistent effect is in `struct ath_hw` INI array pointers and hardware registers, not in this header.

## Dependencies And Integration Points
- Depends on the ath9k INI-table convention and the `u32` type supplied by surrounding kernel headers.
- Integrated by `ar9003_hw.c` through `#include "ar9003_2p2_initvals.h"` and `INIT_INI_ARRAY()`.
- Register addresses and value semantics must match definitions in AR9003 PHY/MAC register headers such as `ar9003_phy.h` and related ath9k hardware code.
- Several later chip initval headers depend on these arrays by aliasing compatible shared tables.

## Risks
- A single incorrect literal can cause failed device bring-up, low RF performance, regulatory-channel malfunction, PCIe power-save instability, or calibration failures.
- Modal table width and row order are part of the ABI expected by ath9k INI writers. Changing a `[][5]` table to the wrong shape or reordering columns would silently program incorrect mode-specific values.
- RX/TX gain tables are tightly coupled to EEPROM/board configuration and power-control assumptions. Using a profile on the wrong board variant can affect transmit power, sensitivity, or compliance.
- Shared aliases from other chip headers mean changes here can affect devices beyond AR9300 2.2.

## Test Signals
- Build coverage should compile ath9k with this header included and catch syntax/shape errors.
- Hardware smoke tests should cover AR9300/AR9003 reset, channel changes, 2.4/5 GHz operation, HT20/HT40, DFS channels, and Japan channel 14 CCK behavior.
- Runtime signals include successful `INIT_INI_ARRAY()` programming, no reset timeouts, stable PCIe suspend/resume when SERDES tables are used, expected noise-floor/calibration completion, and throughput/RSSI sanity across bands.
- Regression checks should compare selected table row counts and modal widths against known-good upstream values before and after any edit.
