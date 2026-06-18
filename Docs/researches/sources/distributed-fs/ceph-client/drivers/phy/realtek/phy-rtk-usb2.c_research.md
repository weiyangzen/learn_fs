# sources/distributed-fs/ceph-client/drivers/phy/realtek/phy-rtk-usb2.c

Purpose: Implements Realtek RTD USB2 PHY initialization and port connect/disconnect tuning for multiple RTD SoCs. It programs paged vendor PHY registers through the DWC2/DWC3 wrapper access register, applies efuse and DT compensation, and exposes debugfs inspection.

Important APIs/types/functions: Key types are `struct phy_cfg`, `struct phy_parameter`, `struct phy_reg`, and `struct rtk_phy`. PHY ops are `rtk_phy_init()`, `rtk_phy_exit()`, `rtk_phy_connect()`, and `rtk_phy_disconnect()`. Important helpers include `rtk_phy_read()`, `rtk_phy_write()`, `rtk_phy_set_page()`, `update_dc_driving_level()`, `update_dc_disconnect_level()`, `do_rtk_phy_toggle()`, `get_phy_data_by_efuse()`, and `parse_phy_data()`.

Control flow: Probe copies the compatible's `phy_cfg`, allocates per-port parameters, maps wrapper/VStatus and PHY access registers through OF, reads optional DT properties for sync-clock inversion, driving level, driving compensation, and disconnect compensation, reads optional `usb-dc-cal` and `usb-dc-dis` nvmem cells, updates cached page data, creates one PHY, registers an OF provider, and creates debugfs files. Init writes configured page0/page1/page2 data for each port unless default parameters are requested, then runs disconnect-side toggle logic. Connect/disconnect callbacks retune sensitivity, driving, and disconnect thresholds per port.

State and persistence: The mutable copied `phy_cfg` caches register data and may be updated by efuse/DT-derived values. Per-port state stores efuse and compensation values plus MMIO pointers. Hardware page registers and sensitivity toggles persist until the next toggle/init or controller reset.

Dependencies and integration points: Depends on generic PHY connect/disconnect callbacks, USB debug root/debugfs, nvmem cells, OF MMIO mapping, sys_soc workaround matching, and Realtek DWC USB wrappers.

Risks: `of_iomap()` mappings are not devm-managed in this file. Port bounds use `index > num_phy`, which allows `index == num_phy` and can address past the allocated array. Shared cached `phy_cfg` data is mutated while iterating ports, so multi-port behavior needs care. Hardware access errors are often logged but do not always abort the full init.

Test signals: Probe every compatible, read debugfs `parameter`, verify nvmem compensation on v1/v2 efuse formats, test one-port and two-port configs, run connect/disconnect callbacks, check out-of-range port handling, inspect page register writes, and enumerate USB2 devices across HS/FS/LS.
