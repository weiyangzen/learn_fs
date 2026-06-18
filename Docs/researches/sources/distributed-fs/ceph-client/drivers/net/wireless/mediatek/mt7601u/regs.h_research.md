# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/regs.h

Purpose: Provides MT7601U/MT76 register offsets, bit fields, queue identifiers, SRAM/key/beacon address maps, and cipher enum values used throughout the driver. It is the hardware register contract for USB control accesses, MCU firmware upload, MAC/PHY configuration, DMA, TX/RX status, and security table programming.

Important definitions: The file covers system and power registers (`MT_ASIC_VERSION`, `MT_CMB_CTRL`, `MT_WLAN_FUN_CTRL`), interrupt and WPDMA registers, USB DMA configuration, PBF/FCE registers, RF/BBP indirect access registers, MAC address/BSSID/filter/timing/protection registers, EDCA/WMM registers, TX power/ALC registers, RX filter bits, statistics/FIFO registers, BBP memory map helpers, WCID address/key/attribute/shared-key tables, beacon SRAM base, and `enum mt76_cipher_type`.

Control flow: No executable control flow exists here, but these constants define every hardware side effect in `usb.c`, `mcu.c`, `phy.c`, MAC code, DMA code, TX status code, and key-management paths. FIELD_GET/FIELD_PREP usage in other files depends on masks in this header matching hardware layout.

State and persistence: Register values configured through these definitions persist in the device until reset, suspend, firmware reinitialization, or explicit rewrite. Security tables and beacon SRAM offsets represent persistent on-chip state for active interfaces.

Dependencies and integration points: Includes `linux/bitops.h` and is included by `mt7601u.h`, which exposes it to the whole driver. Constants are used by vendor request register reads/writes, MCU command payloads, PHY calibration, queue setup, TX status parsing, and key setup.

Risks: Register headers are high-risk for silent regressions: a wrong mask or offset can affect unrelated hardware state with little compiler feedback. Shared names across MT76 variants include comments noting variant-specific meanings, so reuse across chips must be cautious. The incomplete-looking `#define MT_TXOP_CTRL` without value is inert unless referenced but should not be used.

Test signals: Compile coverage for referenced masks, probe ASIC revision, USB DMA/FCE firmware upload, MAC address/filter programming, EDCA configuration, TX status FIFO parsing, and encryption table operation all validate this header indirectly.
