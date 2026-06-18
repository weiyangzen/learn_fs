## sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2400pci.h

### Purpose
`rt2400pci.h` defines the RT2460/RT2400 PCI hardware register map, EEPROM layout, RF/BBP constants, DMA descriptor bitfields, queue sizing constants, and TX power conversion macros used by `rt2400pci.c`.

### Important APIs, Types, And Functions
The header defines RF chip IDs (`RF2420`, `RF2421`), register base/size constants, CSR/TXCSR/RXCSR/ARCSR/PWR/BBP/RF/LED/GPIO fields, EEPROM offsets and field masks, TX/RX descriptor sizes and word field masks, and `TXPOWER_FROM_DEV()`/`TXPOWER_TO_DEV()` conversion macros.

### Control Flow
No executable flow exists, but all driver register manipulation uses these `FIELD32`, `FIELD16`, and `FIELD8` definitions through rt2x00 field helpers. Descriptor fields define when software or NIC owns entries, how packet lengths and PLCP values are set, and how RX status is decoded.

### State, Persistence, And Dependencies
The file models hardware and EEPROM persistent state. It depends on rt2x00 field macros being available before inclusion. EEPROM fields persist MAC address, antenna defaults, RF type, LED mode, tuning, radio button, BBP overrides, and TX power.

### Integration Points
`rt2400pci.c` uses these constants for every register, EEPROM, RF, BBP, descriptor, and power conversion operation. Debugfs also exposes register/eeprom/bbp/rf ranges from these values.

### Risks
Incorrect masks corrupt hardware programming. TX power conversion is reversed relative to other rt2x00 drivers, so misuse can increase or decrease power incorrectly. Descriptor field definitions must match DMA hardware exactly to avoid NIC/software ownership races.

### Test Signals
Register field encode/decode tests, descriptor dump validation against hardware docs, EEPROM parsing fixtures, TX power boundary tests, and debugfs range sanity checks are useful.
