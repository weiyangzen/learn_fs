# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.c

Purpose: debugfs diagnostics and privileged control surface for HFI1 devices. It creates global driver stats files plus per-device files for opcode stats, context stats, QP stats, SDMA engines, receive contexts, PIO contexts, counters, port counters, QSFP/I2C access, ASIC resource flags, 8051 memory, LCB CSR access, expansion-ROM write protection, and fault-injection integration.

Important APIs/functions: `hfi1_dbg_init()`, `hfi1_dbg_exit()`, `hfi1_dbg_ibdev_init()`, and `hfi1_dbg_ibdev_exit()` own debugfs lifetime. The file defines many seq-file iterators (`opcode_stats`, `tx_opcode_stats`, `ctx_stats`, `qp_stats`, `sdes`, `rcds`, `pios`, `sdma_cpu_list`, `driver_stats_names`, `driver_stats`) and read/write handlers for counters, port counters, `asic_flags`, `dc8051_memory`, `lcb`, `i2c1/2`, `qsfp1/2`, `qsfp_dump`, and `exprom_wp`.

Control flow: global init creates `/sys/kernel/debug/hfi1` and driver stats. Per-device init creates `hfi1_<unit>` plus a unit symlink, then registers seq files and per-port files. Reads aggregate statistics from contexts, per-CPU transmit stats, xarray device table, hardware counters, or low-level chip accessors. Writes to ASIC flags, I2C/QSFP, LCB, and expansion-ROM protection parse user input, validate offsets/sizes, acquire chip resources where required, perform hardware access, and release resources on close or release.

State and persistence: persistent state includes the root dentry, per-device debugfs dentries stored on `struct hfi1_ibdev`, hardware resource bits in `ASIC_CFG_SCRATCH`, EEPROM/QSFP/LCB/8051 hardware state, global `exprom_wp_disabled`, and `exprom_in_use` single-open protection. The debugfs files expose live counters and can modify persistent hardware state until reset or driver cleanup.

Dependencies and integration: depends on Linux debugfs/seq_file/fault-inject APIs and on HFI1 modules for QP iteration, SDMA dumps, QSFP/I2C access, chip resources, CSR access, counter readers, and fault debugfs. It is called from driver/module and per-IB-device registration paths.

Risks: debugfs write handlers are intentionally powerful and require root/write permissions, but incorrect validation can touch raw I2C devices, LCB CSRs, ASIC scratch flags, or expansion-ROM write protection. `fault_opcodes_read()` in `fault.c` can expose an empty-bitmap bug, but debugfs here invokes that subsystem. The I2C offset encoding in `ppos` rejects address 0 to catch accidental `cat`/`cp`, but still allows arbitrary device offsets for valid addresses. Resource acquisition on open and release must remain symmetric.

Test signals: debugfs tree creation/removal on probe/remove, repeated open/close of QSFP/I2C/exprom files, counter reads under traffic, context/QP seq iteration under teardown, LCB read/write alignment validation, EPROM write-protect release restoring protection, and `CONFIG_DEBUG_FS=n` build coverage through `debugfs.h` stubs.
