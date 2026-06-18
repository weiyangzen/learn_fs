# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci_mcu.c

Purpose: this file implements PCIe firmware loading and MCU operation setup for MT76x0E devices.

Important functions: `mt76x0e_load_firmware` selects `mediatek/mt7610e.bin` for MT7610 or `mediatek/mt7650e.bin` for combo chips, validates `struct mt76x02_fw_header` size fields, uploads ILM/IVB/DLM regions, triggers firmware, polls `MT_MCU_COM_REG0`, and exports the ethtool firmware version. `mt76x0e_mcu_init` installs mt76x02 MCU ops and marks `MT76_STATE_MCU_RUNNING`.

Control flow: firmware is requested, header and total size are checked, version is logged, combo chips acquire a hardware semaphore, ILM is written through `MT_MCU_ILM_ADDR`, combo IVB is copied to `MT_MCU_IVB_ADDR`, DLM is written after remapping `MT_MCU_PCIE_REMAP_BASE4`, firmware is triggered by `MT_MCU_INT_LEVEL` for combo chips or `MT_MCU_RESET_CTL` for MT7610, and the running bit is polled. The semaphore is released and firmware object freed on all exits.

State and persistence behavior: it writes firmware into MCU RAM and control registers, sets `dev->mt76.mcu_ops`, updates firmware-version reporting, and sets the MCU-running state bit. Firmware contents are transient and reloaded on init/resume.

Dependencies and integration: depends on Linux firmware loader, mt76x02 firmware header format, mt76 MMIO copy helpers, common firmware name macros, and `mcu.h` memory constants. It is called from `pci.c` before common hardware init.

Risks: header length validation protects against malformed blobs, but any mismatch in ILM/DLM offsets or IVB handling prevents boot. Combo semaphore acquisition can time out. Firmware trigger register differs by chip class. The function releases the semaphore even on failure if combo, which is correct but must remain paired.

Test signals: firmware files present, correct version logs, `Firmware running!` debug after poll, ethtool firmware version, successful resume reload, and failure-path tests for missing/truncated firmware. Combo and non-combo chips should both be covered.
