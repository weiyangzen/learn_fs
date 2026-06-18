# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/debugfs.c

Purpose: debugfs controls and diagnostics for MT7925, including register access, firmware logging, runtime PM/deep sleep toggles, TX power tables, queue views, TX stats, PM stats, and chip reset/assert injection.

Important APIs/types/functions: `mt7925_init_debugfs()` registers all entries. `mt7925_reg_get/set()` uses MCU register access; `mt7925_fw_debug_set/get()` toggles firmware log forwarding; `mt7925_txpwr()` queries and prints per-rate power; `mt7925_pm_set/get()` controls runtime PM; `mt7925_deep_sleep_set/get()` controls deep sleep; `mt7925_chip_reset()` triggers reset or firmware assert.

Control flow: debugfs operations acquire mt792x mutex before MCU register/config operations. TX power allocates a `mt7925_txpwr` buffer, queries firmware for the active band, and prints CCK/OFDM/HT/VHT/HE/EHT tables with `127` as not-available. PM writes wake the chip, update user and effective PM flags, reschedule power save, and reject USB. Chip reset value `1` directly resets WFSYS; other values send an `"assert"` chip-config command to collect coredump before reset.

State/persistence: manipulates `dev->fw_debug`, `pm->enable_user`, `pm->enable`, `pm->ds_enable_user`, `pm->ds_enable`, PM statistics, and firmware log/deep-sleep state. Register writes go through firmware and affect hardware state.

Dependencies/integration: depends on debugfs, mt76 debugfs registration, mt7925 MCU helpers (`mt7925_mcu_regval`, `mt7925_mcu_fw_log_2_host`, `mt7925_get_txpwr_info`, `mt7925_mcu_set_deep_sleep`, `mt7925_mcu_chip_config`), and shared mt792x queue/PM debug functions.

Risks: debugfs register writes and chip reset/assert are privileged but can disrupt live traffic. Runtime PM and deep sleep are unsupported on USB and must be kept consistent with monitor mode. TX power output assumes firmware layout matches `struct mt7925_txpwr`.

Test signals: read/write each debugfs attribute, validate PM toggles on PCIe and `-EOPNOTSUPP` on USB, query TX power on all bands, trigger assert/reset in controlled setups, and verify debugfs creation failure handling.
