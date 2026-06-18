# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.h

## Purpose
Defines the ZD1211/ZD1211B chip register map, EEPROM layout, firmware register offsets, bit definitions, chip state object, and chip API used by MAC, USB, and RF code. It is the central hardware contract for BBP/MAC/HMAC register access.

## Important APIs, Types, And Functions
Important constants include address-space bases `CR_START`, `FW_START`, `E2P_START`, helpers `CTL_REG()`, `E2P_DATA()`, `FWRAW_DATA()`, hundreds of `ZD_CR*` and `CR_*` register addresses, interrupt bits, RX filter masks, beacon mode bits, rate masks, encryption modes, retry defaults, `HWINT_ENABLED`, calibration table sizes, EEPROM offsets, and firmware LED/link register values. `struct zd_chip` embeds USB/RF state and EEPROM-derived calibration/policy fields. Inline helpers map between `zd_usb`, `zd_rf`, and `zd_chip`, wrap locked 16/32-bit IO, expose encryption/basic-rate/beacon helpers, and manipulate multicast hash bits.

## Control Flow
No independent runtime flow exists, but the header defines the register and locking contract implemented by `zd_chip.c`: callers either use public wrappers that take `chip->mutex`, or locked wrappers while already holding it. RF drivers call `zd_rfwrite_locked()` and CR write helpers while chip code has PHY registers unlocked.

## State And Persistence
`struct zd_chip` is long-lived for the USB interface lifetime. Its calibration arrays mirror EEPROM contents and are reused for every channel switch. The register constants describe persistent device-side state such as basic/mandatory rate tables, RX filter, group hash, beacon FIFO/semaphore, LED registers, HMAC retry settings, TSF, and encryption mode.

## Dependencies And Integration Points
Includes mac80211 plus local `zd_rf.h` and `zd_usb.h`. It is consumed by every ZD1211RW implementation file and exposes the boundary between mac80211-facing operations and USB vendor command transport.

## Risks
This is a large hardware ABI surface with many vendor-derived magic values. Incorrect address-space assumptions are easy because control registers are byte-addressed while firmware/EEPROM areas are word-addressed. `zd_mc_add_addr()` uses only high bits of the last MAC byte, matching hardware but giving coarse multicast filtering. `zd_chip_reset()` is declared but not implemented in this file set, so users must not assume it is available unless linked elsewhere.

## Test Signals
Build coverage catches missing declarations and bad constants. Runtime validation comes from successful firmware upload, register reads/writes, EEPROM parsing, channel switching, beacon programming, multicast filtering, RX/TX interrupts, and TSF reads on both ZD1211 and ZD1211B variants.
