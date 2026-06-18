# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/table.h

`table.h` declares the RTL8188EE initialization arrays defined in `table.c` and publishes their raw element counts. It exports lengths and extern arrays for PHY, power-group, RF, MAC, and AGC tables.

The header has no control flow. Its length constants govern how runtime PHY loaders walk the arrays, so pair tables and triple tables must be interpreted with the right stride by callers.

It includes `<linux/types.h>` for `u32` and integrates with `table.c`, `sw.c`, and chip-specific PHY configuration. The key risk is length drift: if an array changes without updating the length macro, hardware initialization can truncate data or read beyond the table. Test signals include build coverage, table-size sanity checks, and successful hardware initialization.
