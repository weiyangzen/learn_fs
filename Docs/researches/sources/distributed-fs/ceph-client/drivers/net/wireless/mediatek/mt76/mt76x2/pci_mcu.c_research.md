<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c

Purpose: MT76x2 PCI firmware loader and MCU initialization/restart path. It loads the ROM patch and main firmware over MMIO remap windows, configures MCU ops, and supports watchdog-triggered MCU restart.

Important APIs/types/functions: `mt76x2_mcu_init()`, `mt76pci_load_rom_patch()`, `mt76pci_load_firmware()`, and `mt76pci_mcu_restart()`.

Control flow: ROM patch optionally takes hardware semaphore, checks revision-specific already-applied bit, requests `mt7662_rom_patch.bin`, remaps PCIE base, copies patch to MCU memory, triggers ROM, polls completion, releases semaphore. Firmware requests `mt7662.bin`, validates ILM/DLM size, logs version/build, copies ILM and DLM to revision-specific addresses, handles XTAL option bit, triggers firmware, polls start, and sets wiphy firmware version. MCU init installs send/parse/restart ops, loads patch/firmware, and selects queue. Restart cleans MCU, hard-resets MAC, reloads firmware, and resets WPDMA indices.

State and persistence: MCU firmware memory, COM/CLOCK/semaphore registers, remap base, firmware version string, MCU ops, and WPDMA reset state.

Dependencies/integration: Linux firmware API, shared mt76x02 MCU send/parse/cleanup, mt76x2 MAC reset, EEPROM XTAL option, watchdog reset.

Risks: semaphore timeout/leak, revision-specific patch bit/address, firmware size validation, DLM address differences, and restart failure after queues are reset. Test signals include missing/invalid firmware, already-applied ROM patch, E2 vs E3+ hardware, MCU timeout watchdog restart, and ethtool firmware-version output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c -->
