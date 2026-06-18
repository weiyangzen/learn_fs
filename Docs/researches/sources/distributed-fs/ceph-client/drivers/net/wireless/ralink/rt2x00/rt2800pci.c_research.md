# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800pci.c

## Purpose
Implements the RT2800 PCI/PCIe bus driver. It binds PCI device IDs to the shared rt2x00/RT2800 stack, handles PCI EEPROM and firmware loading, sequences MCU sleep/wakeup requests, and installs the mac80211, rt2x00lib, and rt2800 operation tables for MMIO-backed devices.

## Important APIs, Types, And Functions
Key helpers are `rt2800pci_hwcrypt_disabled()`, `rt2800pci_mcu_status()`, EEPROM bit-bang callbacks for `eeprom_93cx6`, `rt2800pci_read_eeprom_pci()`, efuse/nvmem fallbacks, `rt2800pci_get_firmware_name()`, `rt2800pci_write_firmware()`, `rt2800pci_enable_radio()`, `rt2800pci_set_state()`, and `rt2800pci_set_device_state()`. The important objects are `rt2800pci_mac80211_ops`, `rt2800pci_rt2800_ops`, `rt2800pci_rt2x00_ops`, `rt2800pci_ops`, `rt2800pci_device_table`, and the final `pci_driver`.

## Control Flow
PCI probe calls `rt2x00pci_probe()` with `rt2800pci_ops`. Core probe then invokes RT2800/MMIO probe and queue setup. EEPROM read first tries nvmem, then efuse, then 93cx6 serial EEPROM based on `E2PROM_CSR_TYPE`. Firmware selection uses `rt3290.bin` for RT3290 and `rt2860.bin` otherwise, writes the image at `FIRMWARE_IMAGE_BASE`, toggles PBF system control, and clears mailbox registers. Radio-on first enables the MMIO radio path, clears mailbox state, sends MCU sleep and wake requests, and waits for matching mailbox CIDs. State changes route IRQ on/off to `rt2800mmio_toggle_irq()` and sleep/awake to MCU commands.

## State And Persistence
The module parameter `nohwcrypt` persists for the loaded module and disables hardware encryption. Firmware is cached by rt2x00 core in `rt2x00dev->fw`. EEPROM contents persist in `rt2x00dev->eeprom`; active hardware state is reset or replayed by MMIO/RT2800 init. The PCI device table is static module binding state.

## Dependencies And Integration Points
Depends on Linux PCI, `eeprom_93cx6`, rt2x00 PCI probe/remove/PM helpers, MMIO transport, RT2800 shared library, mac80211 callback implementations from rt2x00 core, and firmware files `rt2860.bin`/`rt3290.bin`. It exports module metadata and firmware requirements to the kernel module loader.

## Risks
MCU mailbox polling has a fixed 200-iteration busy wait and logs only after timeout; failures may leave power state ambiguous. EEPROM source precedence can hide broken efuse or nvmem content. Firmware write/reset sequencing is hardware-sensitive. The PCI device table is broad and conditional by Kconfig, so adding IDs without chipset support can probe unsupported hardware. Hardware crypto disable is global to the module, not per device.

## Test Signals
PCI/PCIe probe across listed chip IDs, EEPROM fallback paths, firmware load for RT3290 and non-RT3290, suspend/resume, rfkill polling, AP/STA operation, hardware crypto on/off via module parameter, tx status interrupt recovery, and `lspci` modalias autoload. Watch for MCU timeout errors and `ieee80211_register_hw()` failures.
