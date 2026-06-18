## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.c

### Purpose
`rt2400pci.c` is the rt2x00 PCI/MMIO driver for Ralink RT2460/RT2400 PCI and PCMCIA wireless devices. It implements chip-specific register access, EEPROM probing, RF/BBP setup, queue and descriptor handling, interrupt tasklets, link tuning, mac80211 callbacks, and PCI module registration.

### Important APIs, Types, And Functions
Important routines include BBP/RF indirect access (`rt2400pci_bbp_read/write()`, `rt2400pci_rf_write()`), EEPROM bit-bang callbacks, LED/rfkill helpers, config handlers (`config_filter`, `config_intf`, `config_erp`, `config_ant`, `config_channel`, `config_ps`), queue handlers, register/BBP initialization, power-state switching, TX descriptor/beacon writing, RX status filling, TX done processing, interrupt/tasklet handlers, EEPROM validation/init, hardware mode probing, and `rt2400pci_probe()`.

### Control Flow
PCI probe delegates to `rt2x00pci_probe()` with `rt2400pci_ops`. Probe reads EEPROM, identifies RF2420/RF2421, sets antenna/rfkill/link-tuning capabilities, builds 2.4 GHz CCK-only channel specs, and marks DMA/ATIM/software-sequence requirements. Radio enable initializes DMA ring registers, core registers, and BBP defaults plus EEPROM overrides. Runtime mac80211 config calls write MAC/BSSID/beacon timing/channel/antenna/power/retry/PS state. Interrupts clear CSR7, schedule tasklets, mask active sources, and tasklets process TX/RX/beacon work before reenabling interrupts.

### State, Persistence, And Dependencies
Persistent device data comes from EEPROM and RF calibration tables. Runtime state lives in `struct rt2x00_dev`, DMA descriptors, skb frame descriptors, tasklets, queue entries, locks, and hardware registers. Dependencies include rt2x00 core/mmio/pci libraries, mac80211, eeprom_93cx6, PCI, LEDs, debugfs, and kernel DMA mapping.

### Integration Points
The file registers `ieee80211_ops`, `rt2x00lib_ops`, `rt2x00_ops`, and a PCI driver for vendor/device `1814:0101`. It uses shared rt2x00 queue, TX/RX, link, debugfs, and mac80211 glue.

### Risks
Hardware ownership bits and descriptor word0 ordering are race-sensitive. Indirect BBP/RF access can time out. IRQ masking/tasklet reenabling must avoid lost interrupts and teardown races. Several ARCSR writes use `ARCSR2_LENGTH` while programming ARCSR3-5 fields, which matches shared bit positions but is brittle. Single global CW handling rejects nonzero queue config.

### Test Signals
Probe/remove, EEPROM width detection, RF2420/RF2421 channel switch, DMA ring ownership, TX success/retry/failure statuses, RX timestamp wrap logic, rfkill GPIO, beacon enable/disable, suspend/resume power states, interrupt storms, and monitor/filter changes are high-value tests.
