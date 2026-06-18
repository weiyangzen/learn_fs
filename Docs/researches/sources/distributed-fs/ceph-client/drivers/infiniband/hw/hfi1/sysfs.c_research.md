# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sysfs.c

## Purpose
`sysfs.c` exposes HFI1 verbs/device state through sysfs under the InfiniBand class device and per-port directories. It provides read-only port mapping data, congestion-control binary attributes, device identity and sensor attributes, a controlled diagnostic reset attribute, and per-SDMA-engine kobjects for CPU affinity and VL reporting.

## Important APIs, Types, and Functions
- `hfi1_get_pportdata_kobj()` maps an IB port sysfs kobject to `struct hfi1_pportdata`.
- `cc_table_bin_read()` and `cc_setting_bin_read()` expose congestion-control table and settings snapshots under the `CCMgtA` port group.
- `cc_prescan_show()` and `cc_prescan_store()` expose a simple on/off administrative congestion-control prescan toggle.
- Generated `sc2vl`, `sl2sc`, and `vl2mtu` attributes expose SC-to-VL, SL-to-SC, and VL-to-MTU mappings.
- Device attributes expose `hw_rev`, `board_id`, `boardversion`, `nctxts`, `nfreectxts`, `serial`, `tempsense`, and write-only `chip_reset`.
- `sde_show()`, `sde_store()`, `sde_sysfs_ops`, and `SDE_ATTR()` implement per-engine SDMA kobject attributes.
- `sde_show_cpu_to_sde_map()`, `sde_store_cpu_to_sde_map()`, and `sde_show_vl()` bridge sysfs to SDMA CPU affinity and VL APIs.
- `hfi1_verbs_register_sysfs()` and `hfi1_verbs_unregister_sysfs()` create and destroy per-engine `sdma%d` kobjects and files.

## Control Flow
The RDMA core consumes `ib_hfi1_attr_group` and `hfi1_attr_port_groups` to create device and port attributes. Attribute show functions derive HFI1 device or port structures from the passed `ib_device`, `device`, or `kobject`, format values with `sysfs_emit()`, and return byte counts or errors. Congestion-control binary reads validate `pos` and `count`, take RCU read lock, fetch `cc_state`, and copy the requested bytes from shadow structures.

SDMA sysfs registration iterates over `dd->num_sdma`, initializes each engine kobject as `sdma%d` under the IB class device kobject, then creates `cpu_list` and `vl` files. Store operations require `CAP_SYS_ADMIN`; `cpu_list` writes are parsed and applied by `sdma_set_cpu_to_sde_map()`. Unregistration drops each kobject reference, relying on kobject cleanup to remove files.

## State and Persistence Behavior
Most attributes expose live in-memory driver state. `cc_prescan_store()` mutates `ppd->cc_prescan`. `chip_reset_store()` triggers `hfi1_reset_device()` only when the write starts with `reset` and a diagnostic client is present. `cpu_list` writes update SDMA per-engine CPU masks and the per-device rhashtable mapping through SDMA code. No sysfs value is persisted by this file across unload or reset.

## Dependencies and Integration Points
The file integrates with RDMA sysfs helpers, HFI1 MAD/congestion structures, HFI1 device and port data, temperature sensing, reset handling, SDMA mapping APIs, Linux capabilities, kobjects, and sysfs attribute groups. It exposes data consumed by administrators, diagnostic tooling, and performance tuning scripts.

## Risks and Edge Cases
Binary read bounds must avoid overflow or out-of-range `pos` handling. RCU-protected congestion state can be absent, returning `-EINVAL`. The `cc_prescan_store()` parser accepts prefixes `"on"` and `"off"` without rejecting other strings, so writes like `"only"` enable it. `chip_reset` is intentionally gated by both string and diagnostic-client checks but remains a powerful side-effecting sysfs write. SDMA kobject registration bailout loops from the current index down to zero; correctness depends on kobject reference behavior for partially initialized entries. `sde_store()` enforces `CAP_SYS_ADMIN`, which is important because CPU affinity affects packet ordering and performance.

## Test Signals
Useful tests include sysfs presence/permissions for device and port groups, partial binary reads with varied offsets and counts, congestion state absent/present cases, `cc_prescan` toggling, valid and invalid `chip_reset` writes, temperature read errors, per-SDMA `vl` output, `cpu_list` parsing for valid/invalid/offline CPUs, and register/unregister failure injection to confirm kobject cleanup.
