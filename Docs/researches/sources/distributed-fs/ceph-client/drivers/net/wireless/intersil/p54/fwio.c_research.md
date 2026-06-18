# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/fwio.c

## Purpose
This file implements p54 common firmware I/O helpers: firmware boot-record parsing, control-frame allocation, EEPROM readback, MAC/filter/scan/power/QoS/LED/key/statistics command construction, and group multicast filter programming.

## Important APIs, Types, and Functions
- `p54_parse_firmware()` parses boot records and exports firmware capabilities.
- `p54_alloc_skb()` builds bounded p54 control SKBs with LMAC headers.
- Command helpers include `p54_download_eeprom()`, `p54_update_beacon_tim()`, `p54_sta_unlock()`, `p54_tx_cancel()`, `p54_setup_mac()`, `p54_scan()`, `p54_set_leds()`, `p54_set_edcf()`, `p54_set_ps()`, `p54_init_xbow_synth()`, `p54_upload_key()`, `p54_fetch_statistics()`, and `p54_set_groupfilter()`.

## Control Flow
Firmware parsing skips leading zero/nonzero preamble, walks boot records, accepts LM86/LM20/LM87 and rejects FMAC/unknown firmware, extracts firmware version, RX memory window, headroom/tailroom, privacy caps, keycache size, RX MTU, LMAC protocol variant, and QoS queue limits. If key cache exists, it allocates a bitmap for hardware RX key slots.

Control helpers allocate a p54 header SKB, append the command-specific payload, fill fields from `p54_common`, and call `p54_tx()`. EEPROM readback serializes with `eeprom_mutex`, points completion handlers at the caller buffer, transmits a readback command using v1 or v2 firmware header format, and waits up to one second. `p54_scan()` is the most complex command builder: it inserts channel frequency, IQ autocal, output limits, PA curve data, RSSI calibration, and firmware-version-dependent rate tails before transmitting.

## State and Persistence Behavior
`p54_parse_firmware()` mutates persistent driver state such as `fw_interface`, `fw_var`, RX ranges, MTU, privacy caps, `tx_stats` limits, queue count, firmware version string, and `used_rxkeys`. Command helpers update cached state such as `phy_idle`, `phy_ps`, `cur_rssi`, and EEPROM completion fields. Firmware-visible command SKBs are transient but may reserve extra firmware memory through `p54_tx_info.extra_len`.

## Dependencies and Integration Points
It depends on mac80211, firmware loader data, p54 ABI definitions from `p54.h`, `eeprom.h`, and `lmac.h`, completions/mutexes, and the bus-provided `p54_common.tx` callback. It integrates with p54 main mac80211 ops, EEPROM parsing, TX/RX feedback in `txrx.c`, and PCI/SPI/USB transports.

## Risks and Edge Cases
Firmware and EEPROM formats vary by `fw_var`; wrong layout selection breaks EEPROM readback or scan setup. `p54_alloc_skb()` rate-limits pending control frames and rejects oversized frames. Missing calibration for a channel aborts scan/channel change. Key upload must match firmware privacy capabilities. Statistics readback deliberately reserves extra device memory without placing payload bytes in the SKB, so address assignment logic must honor `extra_len`.

## Test Signals
Signals include successful firmware parsing, correct firmware interface rejection, EEPROM readback completion, channel changes/scans succeeding for calibrated channels, mac/filter/power/QoS commands updating firmware behavior, key offload success/fallback, LED changes, and periodic statistics completions.
