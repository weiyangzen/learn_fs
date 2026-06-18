<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c

## Purpose
`ppe_debugfs.c` exposes PPE hardware counters through debugfs. It reads, formats, and clears counters for buffer manager, parser, RX/TX ports, VLAN, L2 forwarding, CPU codes, and queue manager activity.

## Important APIs, Types, and Functions
- `enum ppe_cnt_size_type` describes one-word, three-word, and five-word counter table layouts.
- `enum ppe_cnt_type` selects counter families.
- `struct ppe_debugfs_entry` is per-file debugfs private data containing file name/type and PPE device pointer.
- `debugfs_files[]` creates files: `bm`, `parse`, `port_rx`, `vlan_rx`, `l2_forward`, `cpu_code`, `vlan_tx`, `port_tx`, and `qm`.
- `ppe_pkt_cnt_get()` reads counters and reconstructs 32-bit drop counts for five-word tables.
- `ppe_tbl_pkt_cnt_clear()` clears counter locations.
- Family readers print only nonzero counters through `seq_file`.
- `ppe_packet_counter_show()` dispatches reads; `ppe_packet_counter_write()` clears the selected family.
- `ppe_debugfs_setup()` and `ppe_debugfs_teardown()` create/remove `/sys/kernel/debug/ppe`.

## Control Flow
Setup creates a root directory and allocates a private entry for each counter file. Reading a file dispatches by `counter_type` and scans the relevant hardware tables, printing grouped nonzero counters. Writing any data to a file clears that file's associated counters. Teardown recursively removes the root.

## State and Persistence
Debugfs entry memory is devm-allocated. Counter state lives in PPE hardware registers and is mutable through the write handler. The root dentry is stored in `ppe_device`.

## Dependencies and Integration Points
Depends on debugfs, seq_file, regmap, PPE register definitions, and `ppe_device`. It is optional observability for the PPE platform driver and is set up after hardware configuration.

## Risks and Edge Cases
- Files are created with mode `0444` but use `DEFINE_SHOW_STORE_ATTRIBUTE`; if write access is desired, mode and fops expectations should be checked.
- Counter clearing ignores individual regmap write failures.
- Long scans, especially CPU-code and queue tables, can be expensive on slow regmap backends.
- Five-word drop count reconstruction assumes the documented split across words 2 and 3.
- If devm allocation fails mid-loop, setup returns with a partially populated debugfs directory.

## Test Signals
Mount debugfs and read each PPE file after probe, generate traffic to observe nonzero counters, write to clear families where mode permits, and check remove cleans `/sys/kernel/debug/ppe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c -->
