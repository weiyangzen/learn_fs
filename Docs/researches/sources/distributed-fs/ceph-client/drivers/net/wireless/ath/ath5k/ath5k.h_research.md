# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ath5k.h

## Purpose
`ath5k.h` is the central private interface for the ath5k driver. It defines chip IDs, register access helpers, timing constants, hardware revision enums, public driver state, descriptor callback slots, and prototypes shared by the ath5k hardware, PHY, DMA, interrupt, beacon, EEPROM, GPIO, ANI, and mac80211 integration code.

## Important APIs, types, and constants
- Logging and register helpers: `ATH5K_PRINTK`, `ATH5K_INFO/WARN/ERR`, `AR5K_REG_SM`, `AR5K_REG_MS`, `AR5K_REG_WRITE_BITS`, `AR5K_REG_ENABLE_BITS`, `AR5K_REG_DISABLE_BITS`, queue bit helpers, and inline `ath5k_hw_reg_read/write`.
- Hardware identity: PCI device IDs, `enum ath5k_version`, `enum ath5k_radio`, silicon revision defines for MAC, PHY, and radio.
- PHY and timing model: bandwidth modes, antenna modes, slot/SIFS/latency constants, beacon timer constants, power modes, calibration masks, and rate-code mappings.
- TX/RX model: `struct ath5k_tx_status`, `struct ath5k_rx_status`, `struct ath5k_txq`, `struct ath5k_txq_info`, queue type/subtype/id enums, packet type enum, and TX/RX error flags.
- Device state: `struct ath5k_hw` embeds `ath_common`, mac80211 state, channel/rate tables, DMA descriptor storage, RX/TX/beacon lists, locks, tasklets/work items, interrupt masks, rfkill/LED state, capabilities, EEPROM-derived data, calibration timers, ANI state, txpower state, function pointers for descriptors, and bus operations.
- Bus abstraction: `struct ath_bus_ops` supplies cache-size reading, EEPROM reads, and MAC-address reads for PCI/AHB wrappers.

## Control flow and integration
This header is included by most ath5k implementation files and forms the contract between the mac80211-facing code in `base.c`, the low-level hardware helpers in files such as `reset.c`, `dma.c`, `pcu.c`, `phy.c`, `qcu.c`, `desc.c`, and the EEPROM/capability paths. The descriptor callbacks in `ath5k_hw` are assigned during attach and let higher-level TX/RX code call one interface while `desc.c` selects AR5210/5211 2-word or AR5212 4-word descriptor handling. Inline register access switches between normal MMIO and AHB special register routing under `CONFIG_ATH5K_AHB`.

## State and persistence behavior
Most state is runtime kernel memory: descriptor DMA memory, SKB mappings, queue lists, counters, calibration timestamps, ANI variables, txpower tables, current channel/opmode, and EEPROM-derived capability data. Persistent hardware identity and calibration inputs come from EEPROM through `ath5k_hw_nvram_read`; this header stores those values in `ah_capabilities.cap_eeprom` and exposes them to other subsystems. No filesystem persistence is defined here.

## Dependencies
The file depends on Linux kernel MMIO, interrupt, LED, average, cfg80211, and mac80211 headers, plus local ath5k headers `desc.h`, `eeprom.h`, `debug.h`, `ani.h`, and shared ath headers `../ath.h`. Many constants assume register definitions from `reg.h`, although that header is included by implementation files rather than here.

## Risks and edge cases
- Register macros perform read-modify-write operations directly against device MMIO; callers need correct locking and reset/invalid-state discipline.
- The header centralizes many hardware-generation differences. Incorrect `ah_version`, `ah_radio`, or revision classification cascades into queue count, descriptor layout, PHY setup, crypto features, and rate handling.
- `ath5k_hw_hasbssidmask` and `ath5k_hw_hasveol` macros ignore their argument name and reference `ah`, which is fragile if used outside scopes with that variable.
- Fixed descriptor/buffer counts and channel-table sizing make bounds handling important when adding modes or channels.
- AHB register routing for AR2315/AR2317 relies on revision ranges and special physical mappings.

## Test signals
Useful evidence includes successful module probe logs with MAC/PHY/radio names, correct mac80211 band/channel registration, stable TX/RX under reset and channel-switch paths, debugfs register/queue/ANI output, no WARNs from invalid rates or descriptor setup, and correct EEPROM capability interpretation across AR5210, AR5211, AR5212, PCI, and AHB devices.
