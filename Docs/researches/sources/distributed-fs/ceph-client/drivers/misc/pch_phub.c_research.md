# sources/distributed-fs/ceph-client/drivers/misc/pch_phub.c

Purpose: PCI driver for Intel EG20T and ROHM/LAPIS PHUB devices, exposing option-ROM firmware and MAC address sysfs access while applying device-specific prefetch, clock, and interrupt-delay configuration.

Important APIs and types: `struct pch_phub_reg` stores saved registers, MMIO mappings, ROM/MAC offsets, device type, and PCI pointer. Serial ROM helpers include `pch_phub_read_serial_rom()`, `pch_phub_write_serial_rom()`, `pch_phub_read/write_serial_rom_val()`, header setup helpers, and MAC helpers. User-facing paths are binary attribute `pch_firmware` via `pch_phub_bin_read/write()` and `pch_mac` via `show_pch_mac()`/`store_pch_mac()`.

Control flow: probe enables PCI, requests regions, maps BAR1, then branches on `id->driver_data` to create sysfs files, configure prefetch/clock registers, set ROM/MAC offsets, and apply board/OF quirks. ROM reads map the PCI ROM, validate signature `0xAA55`, compute option-ROM size, then copy bytes from serial ROM. Writes map the ROM and program bytes by enabling ROM writes, read-modify-writing aligned words, polling `PHUB_STATUS`, and disabling writes. Remove unregisters sysfs files, unmaps BAR, releases regions, disables PCI, and frees state.

State and persistence: writable serial ROM/MAC/option-ROM content persists in device firmware. Saved register fields are used by suspend/resume helpers to capture and restore PHUB registers when enabled.

Dependencies and integration points: depends on PCI, sysfs bin attributes, DMI board quirks, OF properties such as `intel,eg20t-prefetch`, Ethernet address parsing, and device IDs for Intel/ROHM variants.

Risks and test signals: sysfs writes can permanently modify option ROM and MAC data; bounds and authorization matter. `pch_phub_bin_read()` compares `orom_size < count` rather than remaining `off + count`, so boundary reads deserve review. Remove unconditionally removes both sysfs files even if a given variant did not create both. Tests should cover each device type branch, ROM absent/signature mismatch, timeout in write polling, invalid MAC strings, CM-iTC/Boston quirks, suspend/resume register restoration, and hot-unplug cleanup.
