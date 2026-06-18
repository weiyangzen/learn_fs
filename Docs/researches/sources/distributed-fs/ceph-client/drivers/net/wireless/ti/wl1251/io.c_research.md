# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/io.c

Purpose: Implements address translation and partition programming for wl1251 target memory/register access over an abstract bus interface.

Important APIs and functions: `wl1251_mem_read()`, `wl1251_mem_write()`, `wl1251_mem_read32()`, `wl1251_mem_write32()`, `wl1251_reg_read32()`, `wl1251_reg_write32()`, and `wl1251_set_partition()`. Internal helpers translate logical target addresses through current partition state.

Control flow: Register reads below `REGISTERS_BASE` are interpreted as ACX register table indexes and looked up in `wl1251_io_reg_table`. Memory and register addresses are converted from physical target windows to virtual host-access windows before dispatching to `wl->if_ops->read/write`. `wl1251_set_partition()` clamps total virtual range, prevents overlapping memory/register windows, records physical and virtual bases in `wl`, and writes a `wl1251_partition_set` to `HW_ACCESS_PART0_SIZE_ADDR`.

State and persistence: Maintains `wl->physical_mem_addr`, `wl->physical_reg_addr`, `wl->virtual_mem_addr`, and `wl->virtual_reg_addr`. These are volatile per-device mappings and must match the active firmware partition.

Dependencies and integration points: Depends on `wl1251_if_operations` supplied by SPI or SDIO bus glue. Used by boot, interrupt, RX, TX, EEPROM/NVS, and ACX command paths.

Risks: Invalid ACX register indexes return `-EINVAL`, but callers of `wl1251_reg_read32()` receive that value as a `u32`, so bad indexes can propagate as register data. Partition writes allocate dynamically and log but otherwise return void, so allocation failure cannot be handled by callers. All callers must ensure partitions are correct before target access.

Test signals: Boot failures around chip ID, mailbox, firmware upload, or data-path access often indicate partition translation issues. Bus-level tracing should show partition programming before register/memory reads.
