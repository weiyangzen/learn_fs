
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/sw.c

Purpose: Module and USB driver glue for RTL8192CU/8188CU. It allocates firmware state, declares module parameters and firmware files, wires CU implementations into `rtl_hal_ops`, defines USB interface parameters, maps rtlwifi abstract registers/constants, declares supported USB IDs, and registers the `usb_driver`.

Important APIs/functions: `rtl92cu_init_sw_vars()` initializes DM defaults, allocates a 0x4000 firmware buffer, chooses firmware (`rtl8192cufw_A.bin`, `_B.bin`, or `_TMSC.bin`) based on chip cut/version, and requests firmware asynchronously with `rtl_fw_cb`. `rtl92cu_deinit_sw_vars()` frees firmware memory. `rtl92cu_get_btc_status()` returns false. `rtl8192cu_probe()` delegates to `rtl_usb_probe()`. `module_usb_driver()` registers `rtl8192cu_driver`.

Control flow: On module load, USB IDs are registered. Probe calls rtlwifi USB core with `rtl92cu_hal_cfg`; core invokes HAL ops for chip/version, EEPROM, init, TRX, PHY, security, LED, and DM. Firmware request is asynchronous, so hardware init must handle firmware readiness through rtlwifi callback state. Disconnect delegates to `rtl_usb_disconnect`.

State and persistence: Stores firmware buffer pointer and `max_fw_size`, module parameters `swenc`, `debug_level`, `debug_mask`, USB interface config (`rx_urb_num`, `rx_max_size`, handlers), maps array entries, and the static USB ID table. Disables hub-initiated LPM in the USB driver struct.

Dependencies/integration: Integrates all CU files plus common rtlwifi core, USB, efuse, base, firmware common, PHY common, and mac80211/USB module infrastructure. The `rtl_hal_cfg` maps abstract rtlwifi constants to 8192C register/bit values used by common code.

Risks: Firmware selection depends on `rtlhal.version` being valid before `init_sw_vars`; ordering must be preserved by probe. Firmware allocation failure returns `1` rather than a conventional negative errno. Large USB ID table changes can affect device binding. PM callbacks are commented out, so suspend/resume coverage may be limited. The empty BTC status disables Bluetooth coexistence behavior.

Test signals: Module load/unload, firmware request success/failure, probe on representative Realtek/customer USB IDs, software crypto module parameter, debug parameters, RX/TX URB count behavior, LPM behavior on USB hubs, and full HAL op smoke tests.
