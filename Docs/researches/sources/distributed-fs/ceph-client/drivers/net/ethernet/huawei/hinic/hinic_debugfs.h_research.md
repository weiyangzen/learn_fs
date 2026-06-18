# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_debugfs.h

Declares HiNIC debugfs APIs and PF function-table command/decoded structures. Important definitions are function-table IDs, `HINIC_FUNCTION_CONFIGURE_TABLE_SIZE`, `struct hinic_cmd_lt_rd`, and `struct tag_sml_funcfg_tbl`.

There is no runtime flow here; the bitfield layout drives `hinic_debugfs.c` decoding of firmware table entries. Dependencies include `hinic_dev.h`. Risks are compiler/layout sensitivity of bitfields and stale debugfs entries if lifecycle callers skip removal. Test compile coverage and PF function-table read correctness.
