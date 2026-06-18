# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/sw.c

Purpose: Registers the RTL8192DU USB driver and binds chipset-specific HAL ops, USB endpoint callbacks, module parameters, device IDs, firmware loading, and shared dual-interface data into rtlwifi.

Important APIs/structures: `rtl92du_get_other_intf()` locates the sibling USB interface. `rtl92du_init_shared_data()` shares curve-index arrays and power/hw-init mutexes with a previously probed sibling or allocates them for the first interface. `rtl92du_deinit_shared_data()` frees shared allocations only when the sibling is absent/disconnected. `rtl92du_init_sw_vars()` initializes DM, initial channel, power-save settings, firmware buffer, and asynchronous firmware request. `rtl8192du_hal_ops`, `rtl92du_interface_cfg`, and `rtl92du_hal_cfg` wire local and common rtl8192d callbacks into rtlwifi. `rtl8192du_probe()` delegates to `rtl_usb_probe()`.

Control flow: USB probe enters rtlwifi USB core with `rtl92du_hal_cfg`. Software init allocates/reuses shared calibration state, sets power-save and DM defaults, allocates a 32 KiB firmware buffer, and requests `rtlwifi/rtl8192dufw.bin` asynchronously. Later core operations dispatch through the HAL ops table into PHY, DM, HW, TRX, LED, security, and common rtl8192d helpers.

State and persistence: Live state includes shared `curveindex_2g`, `curveindex_5g`, `mutex_for_power_on_off`, `mutex_for_hw_init`, per-interface DM/PSC fields, initial channel, `disable_amsdu_8k`, `earlymode_enable`, and `pfirmware`. Firmware is loaded through the kernel firmware loader; no driver-written disk state.

Dependencies/integration: Linux USB/module/firmware APIs, mac80211/rtlwifi core, rtl8192d common code, and local PHY/DM/HW/TRX/LED modules. The USB ID table maps multiple Realtek/rebranded VID/PIDs to this config.

Risks: Shared-data lifetime depends on sibling interface disconnect order. If firmware request fails after shared-data allocation, that error path frees firmware but not shared data. Asynchronous firmware loading means later paths must respect firmware readiness.

Test signals: Probe/remove both interfaces in either order, unplug during firmware load, reload module, verify firmware callback, inspect module params, and exercise TX/RX, LEDs, power save, security, and channel switching.
