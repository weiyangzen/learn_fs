# subset-b-004756 ath5k research

This grouped report covers the requested ath5k source files. Each section is source-tree aligned and wrapped with the exact reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/dma.c

## Purpose
`dma.c` owns ath5k hardware DMA control and interrupt-mask/status handling. It starts and stops RX DMA, programs RX/TX descriptor pointers, starts and drains TX queues, adjusts the TX FIFO trigger level, translates hardware interrupt status into `enum ath5k_int`, and initializes/stops DMA during reset or device shutdown. It hides major register differences between AR5210, which lacks QCU/DCU and PISR/SISR registers, and AR5211/AR5212+ hardware.

## Important APIs and Control Flow
The RX path is small: `ath5k_hw_start_rx_dma()` writes `AR5K_CR_RXE`; `ath5k_hw_stop_rx_dma()` writes `AR5K_CR_RXD` and polls for `AR5K_CR_RXE` to clear; `ath5k_hw_set_rxdp()` refuses to change `AR5K_RXDP` while RX is active.

TX queue flow runs through `ath5k_hw_start_tx_dma()` and private `ath5k_hw_stop_tx_dma()`. AR5210 maps logical ath5k queues onto two legacy control bits and `AR5K_BSR`; newer chips use `AR5K_QCU_TXE`, `AR5K_QCU_TXD`, `AR5K_QUEUE_TXDP()`, `AR5K_QUEUE_STATUS()`, and `AR5K_QUEUE_MISC()`. Stop logic enables DCU early termination, waits for QCU disable, polls pending frame counts, and on AR2414+ tries a QUIET-period packet-drop workaround before declaring `-EBUSY`.

Interrupt flow is centered on `ath5k_hw_get_isr()`. AR5210 reads `AR5K_ISR`; newer chips read PISR plus SISR0..4, clear SISRs before selected PISR bits, build `ah->ah_txq_isr_txok_all`, and map beacon, fatal, queue overrun/underrun, and trigger conditions into abstract ath5k bits. `ath5k_hw_set_imr()` disables global interrupts while rewriting masks, preserves per-queue TXURN mask bits, writes IMR/PIMR/SIMR2, updates `ah->ah_imr`, and re-enables `AR5K_IER` if requested.

## State, Dependencies, and Integration
Persistent driver state includes `ah->ah_imr`, `ah->ah_txq[]`, `ah->ah_txq_isr_txok_all`, hardware descriptor pointers, FIFO trigger registers, and pending interrupt registers. Dependencies are register helpers/macros from `reg.h`, debug macros, queue capability state, and timing delays (`udelay`). Integration points include the IRQ handler, reset/stop sequencing, qcu queue setup, beacon queue shutdown, and TX underrun recovery.

## Risks and Test Signals
Risks are hardware hangs during DMA drain, lost interrupts if PISR/SISR clear ordering changes, descriptor-pointer writes while engines are active, and version-specific AR5210 behavior. Test signals include successful suspend/reset without `-EBUSY`, no repeated "queue didn't stop" or "failed to stop RX DMA" debug messages, TX underrun recovery through trigger-level increase, stable beacon queues, and correct per-queue TX completion tasklet scheduling after simultaneous TXOK/TXERR/TXEOL interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.c

## Purpose
`eeprom.c` parses the Atheros EEPROM/NVRAM layout into `ah->ah_capabilities.cap_eeprom`. It validates the header/checksum, decodes supported modes, antenna and RF settings, per-channel power calibration piers, per-rate target powers, conformance test limits, spur channels, RFKill metadata, PCIe SERDES presence, and exposes cleanup plus channel-to-EEPROM-mode mapping. The data it builds is later consumed by PHY, RF register, regulatory, TX power, RFKill, and reset code.

## Important APIs and Control Flow
`ath5k_eeprom_init()` is the top-level initializer. It calls `ath5k_eeprom_init_header()`, `ath5k_eeprom_init_modes()`, `ath5k_eeprom_read_pcal_info()`, `ath5k_eeprom_read_ctl_info()`, and `ath5k_eeprom_read_spur_chans()`. Any `AR5K_EEPROM_READ()` failure returns `-EIO`, so parse failure aborts device initialization.

Header parsing reads magic/protect/regdomain/version/header words, validates custom EEPROM sizes against a fail-safe limit, XOR-checks the data region against `AR5K_EEPROM_INFO_CKSUM`, reads versioned misc words, older OB/DB defaults, HB63 flag, RFKill GPIO/polarity, and SERDES marker. Mode parsing uses `ath5k_eeprom_read_ants()` and `ath5k_eeprom_read_modes()` for 11a/11b/11g offsets, including old-version overrides for threshold/noise defaults.

Power calibration is the file's largest state machine. `ath5k_eeprom_read_pcal_info()` selects one parser by EEPROM version/EEMAP: RF5111, RF5112, or RF2413. Each parser reads version-specific packed bitfields, frequency piers, PD gain masks, and raw curve points, then converts them to common `struct ath5k_pdgain_info` arrays through `ath5k_eeprom_convert_pcal_info_5111()`, `_5112()`, or `_2413()`. Target-rate power parsing and CTL edge parsing convert EEPROM binary channel values via `ath5k_eeprom_bin2freq()`.

## State, Dependencies, and Integration
Persistent state is `struct ath5k_eeprom_info`: mode arrays, power pier arrays, rate power tables, CTL edge tables, spur channels, and dynamically allocated `pd_curves` plus their `pd_step` and `pd_pwr` arrays. `ath5k_eeprom_detach()` releases those dynamic allocations by calling `ath5k_eeprom_free_pcal_info()` for all modes. Dependencies include the bus NVRAM read callback, `eeprom.h` constants/layout macros, `slab.h` allocation, and ath5k debug/error logging.

## Risks and Test Signals
Risks include malformed EEPROM offsets producing invalid loops, signed/unsigned bitfield interpretation errors, memory leaks on partial calibration allocation, selecting the wrong calibration format, unsupported PD-gain masks returning `-EINVAL`, and silent regulatory/power errors from misdecoded CTLs. Test signals include successful attach across EEPROM 3.x/4.x/5.x cards, valid checksum rejection logs for corrupt images, no kmemleak after failed probe/detach, sane channel pier counts, expected RFKill pin/polarity, and TX power calibration matching known hardware dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.h

## Purpose
`eeprom.h` is the EEPROM layout contract for ath5k. It defines offsets, version constants, bitfield extractors, calibration dimensions, RF/regulatory modes, EEPROM read helper macros, and all storage types used by `eeprom.c` and later PHY/TX-power code. It is not just a header for declarations; it encodes the packed on-device data format and the in-memory normalized representation.

## Important Types and Constants
Important offset families include `AR5K_EEPROM_INFO()`, version markers from `AR5K_EEPROM_VERSION_3_0` through `5_3`, `AR5K_EEPROM_MODES_11A/B/G()`, `AR5K_EEPROM_GROUPS_START()`, target power offsets, CTL offsets, RFKill fields, PCIe SERDES marker, and misc-word extractors such as `AR5K_EEPROM_EEMAP()`, `AR5K_EEPROM_TARGET_PWRSTART()`, and `AR5K_EEPROM_CAL_DATA_START()`. `AR5K_EEPROM_OFF()` centralizes old/new offset switching.

Core data types are `struct ath5k_chan_pcal_info_rf5111`, `_rf5112`, `_rf2413`, `struct ath5k_pdgain_info`, `struct ath5k_chan_pcal_info`, `struct ath5k_rate_pcal_info`, `struct ath5k_edge_power`, and `struct ath5k_eeprom_info`. The normalized calibration model stores frequency piers, min/max power, a union of raw RF-specific data, then allocated `pd_curves` for interpolation. `struct ath5k_eeprom_info` aggregates header fields, RF calibration settings, power calibration arrays for 11a/11b/11g, per-rate target powers, CTL edges, noise floor settings, and spur mitigation tables.

## State, Dependencies, and Integration
The `AR5K_EEPROM_READ()` macro depends on an `ah` variable in scope and calls `ath5k_hw_nvram_read()`, returning `-EIO` from the caller on failure. This makes the header tightly coupled to parser functions and their error model. The constants are consumed by EEPROM parsing, PHY setup, regulatory code, RFKill/GPIO setup, spur mitigation, TX power table generation, and capability discovery.

## Risks and Test Signals
Risks come from layout constants being de facto hardware ABI: changing masks, array sizes, version gates, or offset arithmetic can corrupt all downstream calibration. The macro-based read helper hides control flow and requires compatible caller signatures. Test signals include compile coverage of all parsers, attach tests on cards with each EEPROM version/EEMAP, bounds checking of pier/CTL/spur arrays, and comparison of parsed `ath5k_eeprom_info` fields against known-good dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/gpio.c

## Purpose
`gpio.c` controls ath5k GPIO pins and hardware LED pin states. It exposes generic GPIO direction/read/write helpers, configures GPIO interrupts for RFKill, and maps abstract `AR5K_LED_*` states onto `AR5K_PCICFG` LED mode bits. The file covers both GPIO-backed LEDs handled by `led.c` and dedicated LED_0/LED_1 hardware pins controlled directly through PCI configuration bits.

## Important APIs and Control Flow
`ath5k_hw_set_ledstate()` clears existing LED bits and writes a new state. AR5210 has separate LED handling, so the function computes both normal and AR5210 bit patterns. SCAN/AUTH blink pending, INIT turns activity off, ASSOC/RUN selects associated mode, and unknown states fall back to PROM/none.

GPIO helpers are direct register operations with range checks against `AR5K_NUM_GPIO`. `ath5k_hw_set_gpio_input()` and `ath5k_hw_set_gpio_output()` update `AR5K_GPIOCR`; `ath5k_hw_get_gpio()` reads `AR5K_GPIODI`; `ath5k_hw_set_gpio()` updates `AR5K_GPIODO`. `ath5k_hw_set_gpio_intr()` programs GPIO interrupt select/level bits, updates `ah->ah_imr` with `AR5K_IMR_GPIO`, and enables GPIO in `AR5K_PIMR`.

## State, Dependencies, and Integration
Persistent state lives mostly in hardware registers and in `ah->ah_imr`. The file depends on `ath5k_hw_reg_read/write`, `AR5K_REG_ENABLE_BITS`, `AR5K_REG_DISABLE_BITS`, register masks from `reg.h`, and LED/RFKill metadata decoded from EEPROM. Integration points are RFKill switch setup, LED state updates from mac80211 association/scan callbacks, and software LED registration in `led.c`.

## Risks and Test Signals
Risks include invalid GPIO indexes, polarity inversion for RFKill, AR5210 LED bit differences, and `ah->ah_imr` diverging from the hardware IMR if GPIO interrupts are enabled outside normal mask sequencing. Test signals include visible LED transitions for INIT/SCAN/ASSOC, correct GPIO-backed RFKill interrupts on both active-high and active-low switches, no writes for out-of-range GPIOs, and no regression on AR5210 cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/initvals.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/initvals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/led.c

## Purpose
`led.c` integrates ath5k GPIO LEDs with the Linux LED subsystem. It contains a PCI subsystem-device quirk table mapping known laptops/cards to LED GPIO pin and polarity, registers RX/TX LED class devices with mac80211 default triggers, and provides enable/disable/off helpers used during init, remove, suspend, and resume.

## Important APIs and Control Flow
The `ath5k_led_devices[]` table stores matches with encoded `driver_data`; `ATH_PIN()` and `ATH_POLARITY()` unpack it. `ath5k_init_leds()` exits if `CONFIG_MAC80211_LEDS` is disabled or no PCI device is present, matches quirks with `pci_match_id()`, sets `ATH_STAT_LEDSOFT`, configures `ah->led_pin` and `ah->led_on`, calls `ath5k_led_enable()`, then registers `ath5k-%s::rx` and `ath5k-%s::tx` LEDs.

`ath5k_led_enable()` sets the selected GPIO as output and turns it off. `ath5k_led_brightness_set()` maps LED core brightness to `ath5k_led_on()` or `ath5k_led_off()`. `ath5k_unregister_leds()` unregisters RX and TX devices and turns LEDs off. All LED operations check `CONFIG_MAC80211_LEDS` and/or `ATH_STAT_LEDSOFT`.

## State, Dependencies, and Integration
State is stored in `ah->status` bit `ATH_STAT_LEDSOFT`, `ah->led_pin`, `ah->led_on`, and `struct ath5k_led` instances for RX/TX. Dependencies include PCI IDs, the LED class API, mac80211 LED trigger names, GPIO helpers from `gpio.c`, and `wiphy_name()` for naming. Integration points are `ath5k_init_ah()`/deinit through base code and PCI suspend/resume through `ath5k_led_off()`/`ath5k_led_enable()`.

## Risks and Test Signals
Risks include incomplete quirk coverage, wrong polarity causing inverted LED behavior, partial registration failure leaving one LED active, and GPIO conflicts with RFKill or platform wiring. Test signals include correct LED class devices under sysfs, RX/TX triggers toggling the physical LED, off state on unregister/suspend, restored state on resume, and no LED registration attempts on non-PCI/AHB builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/mac80211-ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/mac80211-ops.c

## Purpose
`mac80211-ops.c` is the ath5k `struct ieee80211_ops` implementation. It translates mac80211 callbacks into ath5k queueing, interface bookkeeping, channel/power/retry configuration, beacon and BSSID updates, multicast/RX filter programming, hardware key programming, TSF access, survey reporting, antenna selection, and TX ring sizing.

## Important APIs and Control Flow
`ath5k_tx()` validates skb queue mapping and queues frames through `ath5k_tx_queue()`. Interface add/remove callbacks maintain `ah->nvifs`, AP/adhoc/mesh counts, beacon-buffer ownership (`bcbuf`, `bslot`, `avf->bbuf`), opmode, and BSSID mask/opmode. Adhoc is deliberately restricted to a single interface.

`ath5k_config()` handles channel changes via `ath5k_chan_set()`, TX power through `ath5k_hw_set_txpower_limit()`, retry limit propagation to all queues, and antenna mode restore. `ath5k_bss_info_changed()` responds to BSSID, beacon interval, slot timing, association, beacon content, and beacon enable changes, updating hardware BSSID, beacon filter, LED state, and beacon timers.

Filtering is split between `ath5k_prepare_multicast()` hash generation and `ath5k_configure_filter()` hardware programming. The latter preserves PHY error bits, supports mac80211 FIF flags, adds per-opmode filters, enables promiscuous mode for multiple STA interfaces, then writes RX and multicast filters. `ath5k_set_key()` handles supported WEP/TKIP/CCMP hardware keys and pushes IV/MMIC/management-TX policy back to mac80211. Remaining callbacks expose stats, EDCA queue config, TSF, survey counters, coverage class, antenna masks, and ring parameters.

## State, Dependencies, and Integration
Most mutations are protected by `ah->lock`; beacon updates also use `ah->block`. Persistent state includes interface counts, `ah->opmode`, `ah->assoc`, beacon buffers, BSSID/AID in `ath_common`, `ah->filter_flags`, `ah->fif_filter_flags`, TX queue limits, antenna mode, retry limits, survey counters, and LED state. Dependencies include mac80211/cfg80211 types, ath common key/regd helpers, base transmit/beacon/channel code, PCU functions, and hardware queue APIs.

## Risks and Test Signals
Risks include beacon-buffer leaks on add/remove errors, invalid multi-interface mode combinations, RX filter over/under-permissiveness, key offload mismatches, locking regressions, and ring size changes racing active TX. Test signals include multi-VIF AP/STA smoke tests, adhoc rejection behavior, association LED/filter changes, multicast reception, hardware crypto fallback, survey counter monotonicity, EDCA queue updates, and no stopped queue deadlock after `set_ringparam()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/mac80211-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pci.c

## Purpose
`pci.c` is the PCI bus binding for ath5k. It declares supported PCI IDs, implements PCI EEPROM and MAC address access for ath bus ops, sets up PCI device resources and DMA constraints, allocates the mac80211 hardware object, calls core ath5k initialization, and tears everything down on remove. It also handles small suspend/resume LED and PCI config fixups.

## Important APIs and Control Flow
`ath5k_pci_id_table[]` matches AR5210/5211/5212 and compatible PCI/PCIe devices. `ath5k_pci_read_cachesize()` reads PCI cache line size with a fallback to `L1_CACHE_BYTES >> 2`. `ath5k_pci_eeprom_read()` performs hardware-version-specific EEPROM reads: AR5210 enables `AR5K_PCICFG_EEAE` and reads from mapped EEPROM address space, while newer chips program `AR5K_EEPROM_BASE` and trigger `AR5K_EEPROM_CMD_READ`, polling status until done or timeout. `ath5k_pci_eeprom_read_mac()` validates and copies the MAC from EEPROM words 0x1d..0x1f.

`ath5k_pci_probe()` disables PCIe L0s, enables the device, requires 32-bit DMA, fixes cache line and latency timer, enables bus mastering, disables retry timeout register 0x41, reserves and maps BAR0, allocates `ieee80211_hw`, populates `struct ath5k_hw`, and calls `ath5k_init_ah()` with `ath_pci_bus_ops`. Error paths unwind in reverse order. `ath5k_pci_remove()` calls `ath5k_deinit_ah()`, unmaps/release/disables PCI, and frees the mac80211 object.

## State, Dependencies, and Integration
State includes PCI driver data (`ieee80211_hw`), `ah->pdev`, `ah->dev`, `ah->irq`, `ah->devid`, and `ah->iobase`. Dependencies include Linux PCI, DMA mask, mac80211 allocation, ath common bus ops, register helpers, EEPROM layout macros, and core `base.c` init/deinit. `module_pci_driver()` wires this into the kernel PCI driver model.

## Risks and Test Signals
Risks include BAR mapping failures, unsupported DMA mask, EEPROM read timeout, bad MAC validation, incomplete error unwinding, and resume losing PCI retry-timeout configuration. Test signals include probe/remove under fault injection, valid MAC assignment, successful EEPROM checksum parsing through the bus ops, lspci ID coverage, suspend/resume with LEDs restored, and no resource leaks after repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pcu.c

## Purpose
`pcu.c` controls ath5k Protocol Control Unit behavior: frame duration/ACK timing, MIB counter accumulation, station/BSSID/multicast/RX filters, TSF and beacon timers, coverage class timing, RX PCU enable/disable, operating mode, and PCU initialization. It bridges mac80211 state to hardware registers that implement 802.11 protocol behavior.

## Important APIs and Control Flow
Timing helpers include `ath5k_hw_get_frame_duration()`, which extends mac80211 duration calculation for turbo/half/quarter rate modes, `ath5k_hw_get_default_slottime()`, and `ath5k_hw_get_default_sifs()`. `ath5k_hw_write_rate_duration()` fills AR5212 rate-duration registers using either high ACK rates or base CCK/OFDM rates. ACK/CTS timeout setters validate against field width before writing `AR5K_TIME_OUT`.

Filter and identity APIs include `ath5k_hw_set_lladdr()`, `ath5k_hw_set_bssid()`, `ath5k_hw_set_bssid_mask()`, `ath5k_hw_set_mcast_filter()`, `ath5k_hw_get_rx_filter()`, and `ath5k_hw_set_rx_filter()`. RX filter setup handles AR5212 PHY error filters and AR5210 radar-by-promiscuous fallback.

Beacon/TSF control includes a careful `ath5k_hw_get_tsf64()` double-read under local IRQ disable, `ath5k_hw_set_tsf64()`, `ath5k_hw_reset_tsf()`, `ath5k_hw_init_beacon_timers()`, `ath5k_hw_check_beacon_timers()`, and `ath5k_hw_set_coverage_class()`. `ath5k_hw_set_opmode()` maps NL80211 AP/STA/adhoc/mesh/monitor modes to `AR5K_STA_ID1`, `AR5K_CFG`, and AR5210 beacon-control bits. `ath5k_hw_pcu_init()` restores BSSID, opmode, rate durations, RSSI/BMISS thresholds, MIC/QoS NOACK settings, coverage timing, and ACK bitrate policy.

## State, Dependencies, and Integration
Persistent state is split between registers and software fields: `ath_common` MAC/BSSID/AID/mask, `ah->stats`, `ah->survey`, `ah->ah_current_channel`, `ah->ah_bwmode`, `ah->ah_short_slot`, `ah->ah_coverage_class`, `ah->opmode`, `ah->nvifs`, `ah->ah_ack_bitrate_high`, and RX filter bits. Dependencies include mac80211 rates/channels, ath common cycle counters, unaligned helpers, register macros, and reset/beacon/config paths.

## Risks and Test Signals
Risks include TSF inconsistent reads, wrong beacon timer windows after IBSS TSF merges, RX filter mistakes affecting ACK/radar/PHY-error behavior, incorrect duration math for non-default bandwidths, and opmode bit drift across AR5210 versus AR5212. Test signals include stable IBSS without ramping latency, correct beacon timing in AP/mesh/STA modes, survey counters accumulating, ACK timeout/rate-duration sanity, BSSID mask behavior with multi-VIF, and RX filter changes matching monitor/AP/STA expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pcu.c -->
