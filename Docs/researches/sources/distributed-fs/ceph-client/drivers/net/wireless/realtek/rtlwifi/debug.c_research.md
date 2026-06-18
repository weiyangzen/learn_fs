# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.c

## Purpose
Optional `CONFIG_RTLWIFI_DEBUG` implementation. It provides filtered trace printing, hex dumps, top-level and per-device debugfs directories, register/CAM/BT-coex dumps, and debugfs write hooks for MAC/BB registers, H2C commands, and RF registers.

## Important APIs, Types, And Functions
`_rtl_dbg_print()` and `_rtl_dbg_print_data()` implement debug macros. `struct rtl_debugfs_priv` binds debugfs files to callbacks and selector data. Dump callbacks cover MAC pages, BB pages, RF paths, CAM entries, and BT coexistence. Lifecycle APIs are `rtl_debug_add_one()`, `rtl_debug_remove_one()`, `rtl_debugfs_add_topdir()`, and `rtl_debugfs_remove_topdir()`.

## Control Flow
Probe creates a per-device directory named by MAC address. Reads use seq_file callbacks to read live MMIO/BB/RF/CAM state. Writes parse short hex strings then call `rtl_write_*`, `fill_h2c_cmd`, or `rtl_set_rfreg()`.

## State And Persistence
Global `debugfs_topdir` and static per-file private objects hold debugfs state. The exposed values are live hardware state; writes are immediate and not persistent across reset.

## Dependencies And Integration Points
Uses debugfs, seq_file, register accessors, CAM constants, chip maps, H2C fill ops, RF helpers, BT coexistence ops, and probe/disconnect hooks in `pci.c`.

## Risks
Write files can corrupt hardware state with minimal validation. Static private objects storing `rtlpriv` are fragile for multi-device setups. Live dumps can race normal hardware programming.

## Test Signals
Debug-enabled build, directory create/remove, safe register/CAM/RF/BT reads, malformed write rejection, valid write effects, and disconnect cleanup.
