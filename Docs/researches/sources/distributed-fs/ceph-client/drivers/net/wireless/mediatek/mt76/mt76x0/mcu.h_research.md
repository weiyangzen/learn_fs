# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mcu.h

Purpose: this header defines MT76x0 MCU memory-map constants, calibration command IDs, bus-specific MCU init prototypes, and a simple firmware-running probe.

Important definitions: `MT_MCU_IVB_SIZE` is 0x40, `MT_MCU_DLM_OFFSET` is 0x80000, and `MT_MCU_MEMMAP_RF` is 0x80000000. `enum mcu_calibrate` assigns firmware calibration commands such as `MCU_CAL_R`, `MCU_CAL_RXDCOC`, `MCU_CAL_LC`, `MCU_CAL_TXIQ`, `MCU_CAL_VCO`, and `MCU_CAL_FULL`. Prototypes are `mt76x0e_mcu_init` and `mt76x0u_mcu_init`. Inline `mt76x0_firmware_running` reads `MT_MCU_COM_REG0`.

Control flow and integration: `pci_mcu.c` implements `mt76x0e_mcu_init`; USB code implements `mt76x0u_mcu_init`. `phy.c` uses the calibration enum for `mt76x02_mcu_calibrate` calls and uses `MT_MCU_MEMMAP_RF` for USB RF register access through MCU register-pair commands.

State and persistence behavior: constants address MCU memory and RF register maps; calibration commands alter firmware/hardware state at runtime but are not persisted by this header.

Dependencies: it includes `../mt76x02_mcu.h` for shared MCU command helpers and forward-declares `struct mt76x02_dev`.

Risks: memory-map constants must match firmware loaders and register-pair access. Calibration numeric IDs are firmware ABI values; changing them breaks PHY calibration.

Test signals: firmware boot should set `MT_MCU_COM_REG0` to 1, RF register-pair accesses should work on USB, and calibration commands should complete without errors during init/channel changes.
