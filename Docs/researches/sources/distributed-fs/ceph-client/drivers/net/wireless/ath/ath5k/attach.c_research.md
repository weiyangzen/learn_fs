# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/attach.c

## Purpose
`attach.c` performs early hardware attach for an ath5k device. It identifies the MAC/radio generation, validates support, performs a register POST, initializes EEPROM and capability data, configures selected PCIe power-save registers, initializes common addressing/opmode state, and tears down hardware-private attach resources on detach.

## Important APIs and functions
- `ath5k_hw_post(struct ath5k_hw *ah)`: writes variable and static test patterns to `AR5K_STA_ID0` and `AR5K_PHY(8)`, verifies readback, and restores original values.
- `ath5k_hw_init(struct ath5k_hw *ah)`: top-level hardware init used from `ath5k_init_ah`.
- `ath5k_hw_deinit(struct ath5k_hw *ah)`: marks the device invalid, frees RF banks, and detaches EEPROM state.

## Control flow
`ath5k_hw_init` seeds defaults such as bandwidth, retry limits, antenna mode, ANI mode, noise floor, and current channel. It reads the silicon revision with `ath5k_hw_read_srev`, classifies `ah_version` and `ah_mac_version`, then initializes descriptor function pointers via `ath5k_hw_init_desc_functions`. It wakes and resets the NIC with `ath5k_hw_nic_wakeup`, reads PHY/radio revisions, and maps the radio to RF5110/RF5111/RF5112/RF2413/RF5413/RF2316/RF2317/RF2425 using radio, MAC, and PHY revision fallbacks.

Unsupported chips in the AR5416-to-before-AR2425 range are rejected. The POST runs after support filtering. Newer Hainan and later chips receive the PCI retry fix. EEPROM initialization follows, then AR5212 PCIe devices get a sequence of SERDES writes, influenced by `ee_serdes`, and a SERDES reset. Capabilities are computed by `ath5k_hw_set_capabilities`; crypto limits are filled into `ath_common`; AES-CCM and combined MIC support are enabled based on revision and EEPROM bits. The function clears the MAC address until interface creation, sets broadcast BSSID, applies opmode, initializes RF gain and noise-floor history, and turns on hardware LEDs.

## State and persistence behavior
The function writes persistent-in-session state into `struct ath5k_hw` and `struct ath_common`: version/radio fields, capability flags, crypto capabilities, EEPROM info, RF gain/noise calibration state, initial opmode/BSSID, and LED state. It reads persistent EEPROM contents but does not write them. Hardware registers are modified during wakeup, POST, PCIe SERDES setup, retry-fix enablement, opmode/BSSID setup, and LED initialization.

## Dependencies and integration points
This file depends on PCI helpers, `reg.h`, EEPROM code, descriptor setup in `desc.c`, capability logic in `caps.c`, PHY helpers for radio revision/RF gain/noise history, PCU address/opmode helpers, LED helpers, and shared ath crypto state. It is called from the broader mac80211 attach path in `base.c` after IRQ/common bus state is prepared but before the hardware is registered with mac80211.

## Risks and edge cases
- POST writes to live registers and returns immediately on mismatch without restoring the current register in that failing iteration, so callers depend on later reset/error unwind.
- Radio identification is revision-sensitive and contains several fallback heuristics; misclassification can select wrong PHY/radio programming.
- PCIe SERDES writes are magic constants and must stay limited to AR5212 PCIe devices.
- Unsupported-chip filtering excludes AR5416/AR5418-era devices while allowing AR2425 and later matching code paths.
- `ath5k_hw_deinit` assumes interrupts are already down; callers must order detach correctly.

## Test signals
Probe should log expected AR and RF names, reject unsupported silicon with `-ENODEV`, initialize EEPROM without error, expose correct crypto capabilities, preserve stable register access after POST, and cleanly unload without leaks or IRQ activity after `ath5k_hw_deinit`. PCIe devices should resume from link power states without SERDES-related failures.
