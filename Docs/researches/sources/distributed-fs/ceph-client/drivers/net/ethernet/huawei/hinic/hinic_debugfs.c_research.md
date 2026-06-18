# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.c

Creates HiNIC debugfs diagnostics for SQs, RQs, and PF function-table fields. Public lifecycle APIs add/remove per-queue debug entries, initialize/uninitialize SQ/RQ/function-table directories, initialize per-device debug roots, and register/unregister the global debugfs root.

Reads dispatch through `hinic_dbg_cmd_read()` using `struct hinic_debug_priv`. SQ/RQ values expose queue IDs, producer/consumer indexes, hardware completion pointers, and MSI-X entries. PF function-table reads allocate a `hinic_cmd_lt_rd`, issue `HINIC_PORT_CMD_RD_LINE_TBL`, decode `tag_sml_funcfg_tbl`, and report valid/rx_mode/mtu/rq_depth/queue_num.

State is held in debugfs dentries and `hinic_debug_priv` objects referenced from queues or device. Dependencies are debugfs, HiNIC queue structs, port management commands, and `hinic_dev.h`. Risks are weak debugfs creation error handling, management-command load on repeated reads, PF/VF differences, and lifecycle pairing. Test debugfs tree creation/removal and live reads under traffic.
