# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_phy.h

## Purpose
`ar9003_phy.h` is the AR9003 PHY register map and field-definition header. It gives the implementation files symbolic names for channel, MRC, AGC, synthesizer, per-chain, global, RTT, watchdog, PAPRD, BT coexistence, and 65 nm radio registers. It is foundational for `ar9003_phy.c`, `ar9003_paprd.c`, `ar9003_rtt.c`, MCI/AIC code, and calibration routines.

## Important APIs, Types, and Defines
This header exports macros rather than functions. Register regions include `AR_CHAN_BASE`, `AR_MRC_BASE`, `AR_AGC_BASE`, `AR_SM_BASE`, per-chain channel/AGC/SM bases, and `AR_GLB_BASE`. Dynamic macros such as `AR_PHY_TEST(_ah)`, `AR_PHY_CHAN_INFO_MEMORY(_ah)`, `AR_PHY_PAPRD_TRAINER_CNTL*(_ah)`, `AR_PHY_RTT_TABLE_SW_INTF_B(i)`, and `AR_PHY_65NM_RXRF_AGC(i)` encode chip-revision or chain-dependent offsets.

Major field groups cover spur mitigation (`AR_PHY_TIMING11_*`, pilot/channel/spur masks), ANI and signal detection (`AR_PHY_SFCORR*`, `AR_PHY_FIND_SIG*`, `AR_PHY_TIMING5_*`), radar/DFS (`AR_PHY_RADAR_*`), antenna diversity (`AR_PHY_MC_GAIN_CTRL`, `AR_ANT_DIV_*`), spectral scan (`AR_PHY_SPECTRAL_SCAN_*`), radio retention (`AR_PHY_RTT_*`), baseband watchdog (`AR_PHY_WATCHDOG_*`), PAPRD control/trainer/table fields, BT coexistence LNA-diversity fields, and manual peak-detector/radio AGC fields.

## Control Flow
There is no runtime control flow, but the macro layout directly shapes control flow in implementation files. Channel setup uses synth, mode, active, RX delay, chainmask, and delta-slope definitions. PAPRD setup/training uses the PAPRD control, trainer, status, memory-table, PA gain, TX power, thermal/voltage, forced-gain, and channel-info macros. RTT uses `AR_PHY_RTT_CTRL` and the software table-interface macros. Watchdog code decodes state-machine fields with the watchdog masks. BT antenna diversity and MCI observation use global and coexistence register definitions.

## State and Persistence Behavior
The header does not hold state. It defines the register addresses and bit masks used to create hardware state. Because many definitions are revision-dependent macros, the same source operation can write different offsets on AR9485, AR9561, AR9462, AR9565, and related chips. This means hardware state persistence across reset depends on the caller using the correct revision predicate and reprogramming all required fields.

## Dependencies and Integration Points
The header assumes access to revision predicates and bitfield helpers such as `AR_SREV_*`, `SM()`, and `MS()` from the ath9k hardware layer. It is included by PHY, PAPRD, RTT, MCI, calibration, eeprom, and AIC files. It bridges high-level driver operation tables to raw hardware registers and is also indirectly part of debug/test behavior because watchdog and spectral/radar field decoding depends on these masks.

## Risks
Register headers carry structural risk: a wrong address, mask, shift, or revision predicate can silently program the wrong hardware field. Several macros reference an `ah` identifier inside their expression rather than only their formal parameter, which requires callers to have the expected variable name in scope. Dynamic offsets must stay synchronized with silicon revisions. Duplicated or nearby definitions, such as RX delay and multiple per-chain TPC symbols, can be easy to misuse. PAPRD and RTT definitions are tightly coupled to table sizes and packed data fields in other headers.

## Test Signals
Compile coverage across supported chip revisions is important because macro expressions depend on revision predicates. Runtime signals include successful channel bring-up, correct per-chain register writes, valid PAPRD training status/table programming, working RTT restore, spectral scan completion, decoded watchdog fields, and functioning BT antenna diversity. Hardware register dumps around reset and calibration are the most direct validation that these definitions align with silicon.
