# Research: subset-b-004757

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/phy.c

## Purpose

`phy.c` is the ath5k hardware layer for PHY and RF programming. It owns channel programming, RF-bank construction, gain and noise calibration, I/Q correction, spur mitigation, antenna selection, and transmit power table generation for AR5210/AR5211/AR5212-era Atheros radios. The code is highly hardware-specific and bridges mac80211 channel/rate concepts, EEPROM calibration data, and direct register writes through `ath5k_hw_reg_*` helpers.

## Important APIs, Types, and Functions

Externally visible entry points include `ath5k_hw_radio_revision()`, `ath5k_channel_ok()`, `ath5k_hw_chan_has_spur_noise()`, `ath5k_hw_phy_disable()`, `ath5k_hw_rfgain_opt_init()`, `ath5k_hw_gainf_calibrate()`, `ath5k_hw_init_nfcal_hist()`, `ath5k_hw_update_noise_floor()`, `ath5k_hw_phy_calibrate()`, `ath5k_hw_set_antenna_switch()`, `ath5k_hw_set_antenna_mode()`, `ath5k_hw_set_txpower_limit()`, and `ath5k_hw_phy_init()`.

Core internal helpers are grouped by hardware function. `ath5k_hw_rfb_op()` edits packed RF-bank fields described by `struct ath5k_rf_reg`; `ath5k_hw_rfregs_init()` selects RF-bank templates from `rfbuffer.h`, patches them using EEPROM fields, gain tables, bandwidth mode, and radio revision, then writes the resulting banks to hardware. Channel-specific helpers convert frequencies into radio synthesizer values for RF5110, RF5111, RF5112-class radios, and RF2425/AR2417-class radios. TX power helpers interpolate EEPROM calibration piers into PCDAC or PDADC tables and rate power indices.

The file depends heavily on `struct ath5k_hw` state: `ah_radio`, `ah_version`, `ah_mac_srev`, `ah_phy_revision`, `ah_bwmode`, `ah_current_channel`, `ah_rf_banks`, `ah_offset`, `ah_gain`, `ah_nfcal_hist`, and `ah_txpower`. EEPROM-derived inputs come from `struct ath5k_eeprom_info`, including OB/DB bias, XPD/PD gains, per-channel calibration piers, rate target powers, CTL edge powers, spur channels, and noise floor thresholds.

## Control Flow

The main initialization flow is `ath5k_hw_phy_init()`. It validates fast channel switching, optionally obtains RF bus access for a synth-only channel change, programs TX power early, writes OFDM timing and optional spur mitigation, then either finishes the fast path by starting noise-floor calibration or performs full RF initialization. The full path writes initial RF gain registers, constructs and writes RF banks, toggles 802.11b support on RF5111, sets the radio channel, enables the PHY, waits for synthesizer settle, probes ADC readiness, starts AGC/NF and optional I/Q calibration, waits for AGC completion, and restores antenna mode.

The channel path runs through `ath5k_hw_channel()`. It enforces hardware frequency range via `ath5k_channel_ok()`, chooses the radio-specific synthesizer programming routine, applies the channel-14 CCK Japan/world bit, and persists `ah_current_channel`.

Calibration has several separate loops. `ath5k_hw_phy_calibrate()` performs RF5110 full calibration or RF5111+ I/Q result harvesting, requests a PAPD gain probe when a full calibration requires thermal RF-gain tracking, and updates the noise floor if no NF calibration is already active. `ath5k_hw_update_noise_floor()` checks that hardware completed NF sampling, rejects values above EEPROM threshold, stores a rolling history, writes the median back to hardware, then starts the next NF measurement. `ath5k_hw_gainf_calibrate()` reads PAPD probe feedback, corrects CCK and RF5112A readings, validates detector-window range, and transitions RF gain state to `NEED_CHANGE` or back to `ACTIVE`.

TX power programming starts in `ath5k_hw_txpower()`. It selects PCDAC/PDADC table type by radio, reuses cached channel tables when channel and mode match, rebuilds channel power curves otherwise, writes the hardware power table, applies CTL edge limits, computes per-rate power targets, maps target powers to table indices, and writes the four rate-power registers plus optional TPC maxima.

## State and Persistence Behavior

This file mutates persistent driver state stored in `struct ath5k_hw`, not filesystem state. RF bank memory is allocated lazily with `kmalloc_array()` and reused across resets. Channel table setup is cached through `ah_txpower.txp_setup`, `txp_offset`, `txp_min_idx`, `txp_pd_table`, and related temporary arrays. Calibration state persists in `ah_cal_mask`, `ah_iq_cal_needed`, `ah_noise_floor`, `ah_nfcal_hist`, and `ah_gain.g_state`/`g_step_idx`/threshold fields. Antenna mode and selected antennas persist in `ah_ant_mode`, `ah_def_ant`, and `ah_tx_ant`.

Register writes are stateful hardware side effects. Many operations rely on prior reset state or EEPROM initialization: `ath5k_hw_phy_init()` explicitly assumes a warm reset state, and RF/TX power paths assume EEPROM calibration arrays and capability ranges are populated.

## Dependencies and Integration Points

The file includes Linux delay, allocation, sort, and unaligned access helpers, plus local ath5k headers `ath5k.h`, `reg.h`, `rfbuffer.h`, `rfgain.h`, and `../regd.h`. It integrates with mac80211 types such as `struct ieee80211_channel`, `enum nl80211_band`, `struct ieee80211_supported_band`, and `struct ieee80211_rate`. Regulatory limiting uses `ath5k_hw_regulatory()` and `ath_regd_get_band_ctl()`.

Register definitions from `reg.h` are central: PHY activation, AGC/NF/IQ, RF buffer controls, spur masks, antenna registers, TX power registers, QCU/DCU timing, PCU station bits, and EEPROM access fields are all programmed here. EEPROM parsing and capability setup happen elsewhere but are consumed throughout. Reset code calls `ath5k_hw_phy_init()`, periodic calibration code calls `ath5k_hw_phy_calibrate()` and `ath5k_hw_gainf_calibrate()`, and driver txpower/antenna controls call the exported setters.

## Risks and Edge Cases

The code encodes reverse-engineered radio behavior and many chip-family special cases. Incorrect radio revision checks, bandwidth assumptions, or EEPROM indexes can produce invalid RF-bank values or bad transmit power. `ath5k_hw_rfb_op()` performs bit packing across RF banks; malformed `ath5k_rf_reg` metadata or offsets can silently corrupt RF programming, although there is a boundary check for column, length, and bit range.

Calibration risk is high because several routines deliberately interrupt or alter PHY/RF operation. NF calibration may leave the previous value if hardware does not complete, AGC may time out in noisy environments, and I/Q calibration returns normal non-fatal failures when traffic is insufficient. TX power code must avoid divide-by-zero, table underflow/overflow, negative power offsets, and out-of-bounds PCDAC/PDADC values; the implementation has clamps and extrapolation guards but remains sensitive to malformed EEPROM data.

Fast channel switching risks stale state because it bypasses most RF setup and only starts NF calibration. It must only be used when modulation mode does not change and RF bus grant succeeds. Channel programming comments warn that unsupported frequencies may damage hardware, so callers must honor `ath5k_channel_ok()` and regulatory paths above this layer.

## Test Signals

Useful runtime signals are kernel logs under `ATH5K_DEBUG_CALIBRATE` and `ATH5K_DEBUG_TXPOWER`, calibration timeout messages, noise floor values, I/Q correction values, gain step transitions, and channel out-of-range errors. Hardware validation should cover AR5210, AR5211, AR5212, RF5110/5111/5112/2413/2316/5413/2317/2425 combinations where available, with 2 GHz, 5 GHz, 11b, 11g, 11a, turbo, half-rate, and quarter-rate modes. Behavioral tests should verify reset/channel-change success, txpower limits, rate power table contents, beacon/traffic continuity after calibration, antenna mode effects, and operation on channels with EEPROM spur entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/qcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/qcu.c

## Purpose

`qcu.c` configures ath5k transmit queues and their Queue Control Unit/Distributed Coordination Function Control Unit hardware. It maps driver queue types to hardware queue IDs, stores per-queue software configuration in `ah->ah_txq[]`, programs contention, retry, CBR, ready-time, burst, beacon/CAB/UAPSD behavior, and maintains secondary per-queue interrupt masks.

## Important APIs, Types, and Functions

Public functions are `ath5k_hw_num_tx_pending()`, `ath5k_hw_release_tx_queue()`, `ath5k_hw_get_tx_queueprops()`, `ath5k_hw_set_tx_queueprops()`, `ath5k_hw_setup_tx_queue()`, `ath5k_hw_set_tx_retry_limits()`, `ath5k_hw_reset_tx_queue()`, `ath5k_hw_set_ifs_intervals()`, and `ath5k_hw_init_queues()`.

The main data type is `struct ath5k_txq_info`, stored per queue in `struct ath5k_hw::ah_txq`. Queue type and subtype values come from ath5k enums and WME access categories. Queue flags drive interrupt mask bits and DCU behavior: TXOK/TXERR/TXURN/TXDESC/TXEOL, CBR overrun/underrun, QTRIG, TXNOFRM, backoff policy, fragmentation burst backoff, and ready-time expiration policy.

`ath5k_cw_validate()` is a small but important helper that caps contention windows at 1023 and coerces requested values to power-of-two-minus-one form. This prevents invalid CW values from being written into DCU local IFS registers.

## Control Flow

Queue setup begins with `ath5k_hw_setup_tx_queue()`, which maps logical queue types to hardware queue IDs. AR5210 has only two non-QCU queues, while newer chips use WME subtype IDs for data, fixed IDs for UAPSD, beacon, and CAB queues. The function resets software state, applies optional queue properties, and marks the queue active in `ah_txq_status`.

Queue property updates run through `ath5k_hw_set_tx_queueprops()`, which rejects inactive queues, copies values, clamps AIFS to `0xFC` because larger values can hang the DCU, validates CW min/max, and forces post-frame backoff disable for video/voice data queues and UAPSD.

Hardware programming is done by `ath5k_hw_reset_tx_queue()`. It skips AR5210 and inactive queues, writes DCU local IFS, retry limits, fragmentation wait, sequence-control quirks, optional CBR/ready-time/burst registers, queue-type-specific beacon/CAB/UAPSD scheduling bits, per-queue interrupt mask state, secondary interrupt mask registers, TXNOFRM masks, and a 1:1 QCU-to-DCU mask.

Global initialization is `ath5k_hw_init_queues()`. On AR5211+ it resets every configured hardware queue; on AR5210 it only programs retry limits. It enables turbo IFS behavior for 40 MHz and calls `ath5k_hw_set_ifs_intervals()` when coverage class did not already set timing.

## State and Persistence Behavior

The file persists queue configuration in `ah->ah_txq[]` and interrupt masks in `ah_txq_status`, `ah_txq_imr_txok`, `ah_txq_imr_txerr`, `ah_txq_imr_txurn`, `ah_txq_imr_txdesc`, `ah_txq_imr_txeol`, `ah_txq_imr_cbrorn`, `ah_txq_imr_cbrurn`, `ah_txq_imr_qtrig`, and `ah_txq_imr_nofrm`. These values are then reflected into SIMR0-SIMR4 and TXNOFRM hardware registers during queue reset. `ath5k_hw_release_tx_queue()` marks queues inactive and clears the active-status mask so future operations filter them out.

Pending frame state is read from hardware through `AR5K_QUEUE_STATUS()` and `AR5K_QCU_TXE`. The function returns a boolean-like true when TXE remains set even with no frame count, allowing upper layers to treat the queue as not fully stopped.

## Dependencies and Integration Points

`qcu.c` includes `ath5k.h`, `reg.h`, `debug.h`, and Linux `log2.h`. It uses register helpers and queue bit macros from ath5k headers. The queue register addresses and fields come from `reg.h`, especially QCU status/control registers, DCU local/global IFS registers, retry limits, secondary interrupt masks, and AR5210 no-DCU registers.

The driver/mac80211 integration point is queue creation and WME parameter application. Reset code calls `ath5k_hw_init_queues()` after hardware reset, tx scheduling paths query `ath5k_hw_num_tx_pending()`, and interrupt setup depends on the per-queue masks written here. Timing code relies on PHY/mac helpers such as `ath5k_hw_htoclock()`, `ath5k_hw_get_default_sifs()`, `ath5k_hw_get_frame_duration()`, and `ath5k_hw_get_default_slottime()`.

## Risks and Edge Cases

The code must preserve AR5210 behavior, which lacks QCU/DCU, while programming richer queue hardware on newer chips. Off-by-one queue IDs or queue count mismatches would corrupt unrelated queue registers. AIFS above `0xFC` is explicitly hazardous because it can hang the DCU; CW values must also be normalized before use.

Beacon and CAB queues have timing-sensitive ready-time formulas involving `AR5K_TUNE_SW_BEACON_RESP`, `AR5K_TUNE_DMA_BEACON_RESP`, and `AR5K_TUNE_ADDITIONAL_SWBA_BACKOFF`. Bad ready time can break beacon delivery or buffered broadcast/multicast traffic. Secondary interrupt masks are derived from accumulated software state and active queue masks; stale bits for inactive queues could cause spurious interrupts, while missing bits can hide queue completions or underruns.

`ath5k_hw_set_ifs_intervals()` depends on a current channel and supported-band rate table. It warns and fails when no matching lowest rate exists for the bandwidth mode. Incorrect clock conversion or SIFS/EIFS programming affects contention fairness and ACK timeout behavior.

## Test Signals

Useful signals include queue reset errors, queue pending counts, TXOK/TXERR/TXEOL/TXURN interrupt distribution by queue, beacon/CAB delivery timing, WME access category latency, UAPSD behavior, and absence of DCU hangs under high AIFS/CW inputs. Tests should exercise AR5210 two-queue mode separately from AR5211+ QCU/DCU mode, all queue types, inactive queue release, 40 MHz turbo IFS, and 5/10 MHz rate-flag selection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/qcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reg.h

## Purpose

`reg.h` is the ath5k hardware register map for Atheros AR5210/AR5211/AR5212-era MAC, QCU/DCU, PCU, EEPROM, PHY/RF, and WiSoC platform registers. It defines register addresses, bit masks, shifts, queue-indexed address macros, and version-dependent address aliases used by the rest of the driver.

## Important APIs, Types, and Definitions

This header has no functions or persistent objects. Its important interface is its macro vocabulary. Address families include MAC DMA/control (`AR5K_CR`, `AR5K_CFG`, `AR5K_TXCFG`, `AR5K_RXCFG`), interrupts (`AR5K_ISR`, `AR5K_PISR`, `AR5K_SISR*`, `AR5K_IMR`, `AR5K_PIMR`, `AR5K_SIMR*`), QCU registers (`AR5K_QUEUE_TXDP()`, `AR5K_QCU_TXE`, `AR5K_QUEUE_CBRCFG()`, `AR5K_QUEUE_RDYTIMECFG()`, `AR5K_QUEUE_MISC()`, `AR5K_QUEUE_STATUS()`), DCU registers (`AR5K_QUEUE_QCUMASK()`, `AR5K_QUEUE_DFS_LOCAL_IFS()`, `AR5K_QUEUE_DFS_RETRY_LIMIT()`, `AR5K_QUEUE_DFS_CHANNEL_TIME()`, `AR5K_QUEUE_DFS_MISC()`), reset/sleep/PCI/GPIO registers, EEPROM access registers, PCU registers, key table sizing, PHY/RF registers, TX power tables, and WiSoC reset/enable registers.

Several macros intentionally depend on a live `ah` variable to choose AR5210 versus AR5211+ addresses or flags, for example `AR5K_EEPROM_DATA`, `AR5K_EEPROM_STATUS`, `AR5K_STA_ID1_PCF`, `AR5K_USEC`, `AR5K_BEACON`, `AR5K_TIMER*`, `AR5K_RX_FILTER`, `AR5K_DIAG_SW`, `AR5K_TSF_L32`, and `AR5K_PHY_FRAME_CTL`. Queue-indexed macros use `AR5K_QUEUE_REG(_r, _q)` to compute per-queue offsets.

## Control Flow

As a header, control flow is indirect. Code in `phy.c`, `qcu.c`, reset, interrupt, EEPROM, GPIO, beacon, and DMA modules reads these definitions to build register values with local helpers such as `AR5K_REG_SM`, `AR5K_REG_MS`, `AR5K_REG_WRITE_BITS`, `AR5K_REG_ENABLE_BITS`, and `AR5K_REG_DISABLE_BITS` from shared headers.

The register map is organized by hardware block. MAC DMA and base interrupt definitions appear first, followed by QCU/DCU scheduling blocks, reset/sleep/PCI/GPIO, EEPROM access, PCU/TSF/beacon/MIB/XR/QoS/key-related registers, then PHY and RF registers. This order mirrors how reset and initialization code tends to bring the device up: DMA and interrupts, queue scheduling, power/reset, EEPROM, PCU, then PHY/RF.

## State and Persistence Behavior

`reg.h` itself stores no state, but its macros define all memory-mapped hardware state manipulated by ath5k. Writes to these addresses persist in device registers until reset, sleep transition, or later driver writes. Read-and-clear interrupt aliases (`AR5K_RAC_PISR`, `AR5K_RAC_SISR*`) have destructive read semantics by design. MIB counters are cleared on read or controlled by `AR5K_MIBC`. EEPROM macros define persistent nonvolatile access paths, although actual read/write sequencing lives elsewhere.

Version-dependent macros are a major state coupling: the same logical register often has different addresses or bit meanings on AR5210 versus AR5211/AR5212. Users must only expand those macros in contexts with a valid `struct ath5k_hw *ah` named `ah`.

## Dependencies and Integration Points

The file includes `../reg.h` for shared register helper macros and uses ath5k hardware version constants defined elsewhere. It is included by most hardware-facing ath5k source files. `phy.c` uses the PHY/RF, spur, antenna, calibration, and TX power definitions. `qcu.c` uses the QCU/DCU, IFS, retry, interrupt mask, and AR5210 no-QCU definitions. EEPROM code uses `AR5K_EEPROM_*`; reset/power code uses reset, sleep, PCI, GPIO, and PCU definitions; interrupt code uses ISR/IMR/SISR/SIMR fields.

The header also integrates older 5210 behavior with newer 5211/5212 behavior through aliases, keeping call sites mostly hardware-family-neutral while still exposing family-specific bits when needed.

## Risks and Edge Cases

This header is high blast radius because a wrong address, mask, or shift changes hardware behavior across many modules. Several definitions are reverse-engineered or annotated with uncertainty, so changes must be treated as hardware behavior changes rather than cosmetic cleanup. Overlapping addresses are intentional in many cases, either because AR5210 and AR5211+ use different blocks at the same offset or because one register has multiple interpretations by radio generation.

Macros that reference `ah` can fail unexpectedly if used outside the local naming convention or in contexts where the version is not initialized. Typographical mistakes in macros are especially risky because they may compile into incorrect register programming; for example rate-table and PHY masks should be cross-checked with all consumers before modification. Queue and interrupt masks represent only a subset of hardware queues in some registers, so callers must respect queue count and QCU/DCU representation limits.

Read-clear registers and MIB counters need careful sequencing to avoid losing interrupt or counter information. EEPROM write macros expose persistent device storage; code using them must enforce status polling and protection semantics.

## Test Signals

Validation signals are mostly integration-level: successful reset, EEPROM reads, interrupt enable/status behavior, queue scheduling, beacon timers, GPIO/rfkill interrupts, MIB counter updates, PHY calibration, channel programming, and TX power table writes across supported chip families. Static review should compare every changed address/mask/shift against consumers and known hardware references. Build coverage should include all files that include `reg.h`, and runtime coverage should include both AR5210-specific aliases and AR5211/AR5212 paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reg.h -->
