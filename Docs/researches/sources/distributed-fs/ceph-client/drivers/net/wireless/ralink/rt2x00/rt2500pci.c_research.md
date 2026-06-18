## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2500pci.c

### Purpose
`rt2500pci.c` is the rt2x00 PCI/MMIO driver for Ralink RT2560/RT2500 PCI and PCMCIA wireless devices. It is structurally similar to rt2400pci but supports OFDM, more RF front ends, optional 5 GHz channels through RF5222, richer descriptor fields, and RT2560-specific tuning.

### Important APIs, Types, And Functions
Important routines include BBP/RF indirect access, EEPROM bit-bang callbacks, rfkill/LED helpers, configuration handlers, RF channel programming with TX power, dynamic link tuning, queue and descriptor operations, register/BBP initialization, power-state switching, interrupt/tasklet handling, EEPROM validation with default repair, RF table selection, hardware-mode probing, and PCI/module registration.

### Control Flow
Probe delegates to `rt2x00pci_probe()` with `rt2500pci_ops`. EEPROM is read and missing antenna/NIC/calibration words are synthesized. RF type is validated among RF2522/2523/2524/2525/2525E/5222, capabilities are set, RSSI offset is read, and channel tables are selected. Radio enable programs queues, MAC/PCI/BBP/autoresponder registers, then BBP defaults and EEPROM overrides. Channel changes program RF registers with RF-specific tuning sequences, channel-14 filter, optional RF4, and TX power. Interrupts clear CSR7, schedule tasklets, mask sources, and tasklets drain TX/RX/beacon work.

### State, Persistence, And Dependencies
Runtime state is in rt2x00 core structures, DMA descriptors, skb metadata, locks, tasklets, and hardware registers. Persistent device configuration is EEPROM plus static RF channel tables. Dependencies are rt2x00 core/mmio/pci, mac80211, eeprom_93cx6, PCI, LEDs, debugfs, and DMA APIs.

### Integration Points
The file registers `ieee80211_ops`, `rt2x00lib_ops`, `rt2x00_ops`, and a PCI driver for `1814:0201`. It uses shared rt2x00 mac80211 callbacks for most operations and supplies chip-specific callbacks for hardware handling.

### Risks
The driver has many RF-specific branches and revision-specific link tuning, so regressions can be hardware-specific. Descriptor word0 ownership ordering is race-sensitive. EEPROM default repair may hide bad hardware data. Probe reads RSSI offset but `rt2500pci_probe_hw()` later sets `rssi_offset = DEFAULT_RSSI_OFFSET`, which may override calibration and is worth checking against intended behavior. The RF5222 channel table has unusual channel ordering around 52/66/60/64 that should match hardware expectations.

### Test Signals
Probe/remove across RF variants, EEPROM fallback fixtures, 2.4/5 GHz channel switching, TX power changes without channel changes, OFDM/CCK RX signal interpretation, dynamic CCA/R17 tuning, rfkill delayed behavior, DMA descriptor ownership, interrupt masking, beacon reload, and suspend/resume are key validation signals.
