# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/dev.c

## Purpose

`dev.c` is the RTL8180/RTL8185/RTL8187SE PCI/CardBus mac80211 driver core. It handles PCI probe/remove, MMIO/PIO mapping, EEPROM parsing, RF frontend selection, DMA ring allocation, interrupt handling, TX/RX descriptor processing, hardware reset/init/stop, mac80211 interface/config callbacks, software beaconing, and filter/basic-rate/ERP configuration.

## Important APIs, Types, and Functions

The module is registered through `module_pci_driver(rtl8180_driver)`. `rtl8180_ops` exposes mac80211 callbacks. `rtl8180_probe()` sets up PCI resources, `ieee80211_hw`, chip-family detection, bands/rates, EEPROM data, RF ops, and registration. `rtl8180_start()` allocates rings, initializes hardware, requests IRQ, and turns on RX/TX. `rtl8180_stop()` disables interrupts/RX/TX, stops RF, powers down analog state, frees IRQ and rings. Data path functions are `rtl8180_tx()`, `rtl8180_handle_tx()`, and `rtl8180_handle_rx()`. Hardware helpers include `rtl8180_write_phy()`, `rtl8180_set_anaparam*()`, `rtl8180_init_hw()`, `rtl8180_conf_basic_rates()`, `rtl8180_conf_erp()`, and `rtl8180_eeprom_read()`.

## Control Flow

Probe enables PCI, requests BARs, requires 32-bit DMA, allocates mac80211 hardware, maps MMIO or PIO, detects chip family from `TX_CONF`, configures queue count and band capabilities, reads EEPROM, selects an RF ops table by RF type, validates/generates the MAC address, then registers with mac80211. Start allocates a 32-entry RX ring and 16-entry TX rings, writes descriptor base addresses, resets and configures MAC registers, performs RF init, sets basic rates/antenna config, installs an IRQ handler, and enables RX/TX. TX maps skb data, fills descriptor fields, assigns sequence numbers when requested, writes flags last with barriers, queues the skb, and kicks the mapped hardware queue. Interrupts dispatch completed TX rings and RX descriptors. RX swaps in a fresh mapped skb before delivering the old skb to mac80211 with rate, signal, TSF, FCS, and preamble metadata.

## State and Persistence Behavior

Persistent device state comes from 93cx6 EEPROM: RF type, carrier-sense threshold, MAC address, channel TX powers, analog parameters, RF parameters, RTL8187SE antenna diversity, crystal, and thermal data. Runtime state is in `struct rtl8180_priv`: MMIO map, RF ops, active vif, spinlock, RX/TX rings and DMA addresses, channel/rate tables, queue parameters, chip family, RX filter mask, slot/ACK timing, analog/RF calibration fields, and sequence number. `struct rtl8180_vif` stores per-interface beacon work and beacon-enable state.

## Dependencies and Integration Points

The driver depends on PCI, DMA mapping, interrupts, `eeprom_93cx6`, mac80211, shared `rtl818x.h` CSR definitions, and RF implementations (`rtl8225`, `rtl8225se`, `sa2400`, `max2820`, `grf5101`). It integrates with mac80211 queue flow control, rx/tx status APIs, BSS change notifications, multicast/filter callbacks, channel config, and TSF reads.

## Risks and Edge Cases

DMA descriptor ownership uses memory barriers and must keep flag writes last; reordering can let hardware read partial descriptors. RX error paths can leak or reuse mappings incorrectly if ring allocation partially fails. RTL8187SE differs in descriptor size, interrupt status width, queue mapping, and MMIO-only support. Software beaconing uses delayed work and the normal data queue rather than a finalized beacon queue, so queue stoppage and timing drift are expected risks. Filter updates toggle bits based on `changed_flags`, so callers must pass correct deltas. EEPROM-derived RF selection rejects unsupported RFs and invalid chip families.

## Test Signals

Validate PCI probe/remove for RTL8180, RTL8185, and RTL8187SE IDs; MMIO fallback behavior; invalid EEPROM MAC fallback; RF type selection; start/stop ring allocation and cleanup; TX queue stop/wake under load; RX descriptor wraparound; interrupt paths for 16-bit and 32-bit status; station and ad-hoc modes; BSSID/basic-rate/ERP changes; multicast/promiscuous/FCS/control filters; software beaconing; and suspend/resume stubs.
