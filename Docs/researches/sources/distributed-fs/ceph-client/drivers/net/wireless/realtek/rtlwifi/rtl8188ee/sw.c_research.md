# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/sw.c

`sw.c` is the RTL8188EE PCI driver glue. It initializes software state, requests firmware, defines module parameters, maps chip-specific registers into rtlwifi common slots, registers the HAL operation table, and binds PCI device ID `0x8179` to `rtl_pci_probe()`.

Important functions are `rtl88e_init_aspm_vars()`, `rtl88e_init_sw_vars()`, and `rtl88e_deinit_sw_vars()`. The init path sets DM defaults, TX/RX configs, interrupt masks, power-save knobs, MSI/ASPM options, firmware buffer allocation, asynchronous firmware request for `rtlwifi/rtl8188efw.bin`, early mode defaults, skb wait queues, and timers. The HAL ops table connects EEPROM, interrupt, hardware lifecycle, beacon/QoS, TX/RX descriptors, channel/bandwidth, RF power, LED, security, BB/RF register access, and watchdog callbacks to common rtlwifi/mac80211 code.

Persistent state lives in `rtl_priv`, `rtl_pci`, `rtl_hal`, `rtl_ps_ctl`, module parameters, firmware buffer storage, and timers. Dependencies include Linux PCI/module/firmware/timer APIs plus rtlwifi core, pci, hw, phy, dm, trx, led, and table components.

Risks include firmware request failure cleanup, timer lifetime, mismatched module parameter defaults/descriptions, incomplete interrupt masks, and incorrect register map entries. Test signals include module load/unload, firmware callback success/failure, probe/remove, suspend/resume, MSI/ASPM toggles, interrupts, association, TX/RX, and hardware security.
