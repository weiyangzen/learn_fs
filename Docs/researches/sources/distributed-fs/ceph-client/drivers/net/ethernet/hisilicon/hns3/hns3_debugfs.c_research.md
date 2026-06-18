# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_debugfs.c

## Purpose

`hns3_debugfs.c` builds the HNS3 debugfs interface. It creates per-device directories and files for traffic management, queue state, descriptor rings, MAC lists, register dumps, flow director state, page pool state, interrupt coalescing, device capabilities/specs, and backend-provided diagnostics. It also registers and unregisters the global HNS3 debugfs root.

## Important Data and Functions

- `hns3_dbgfs_root` stores the global root dentry.
- `hns3_dbg_dentry[]` defines per-device child directories such as `tm`, `tx_bd_info`, `rx_bd_info`, `mac_list`, `reg`, `queue`, `fd`, and `common`.
- `hns3_dbg_cmd[]` maps file names to `enum hnae3_dbg_cmd`, target directory, and init function.
- `hns3_dbg_cap[]` maps user-readable capability names to HNAE3 capability bits.
- `hns3_dbg_coal_info()` reports TX/RX DIM and interrupt moderation state.
- `hns3_dbg_rx_queue_info()` and `hns3_dbg_tx_queue_info()` dump queue MMIO register state.
- `hns3_dbg_queue_map()` reports local queue, global queue, and vector IRQ mapping.
- `hns3_dbg_rx_bd_info()` and `hns3_dbg_tx_bd_info()` dump descriptor contents for a selected queue.
- `hns3_dbg_dev_info()` reports device capabilities and firmware-derived specs.
- `hns3_dbg_page_pool_info()` reports RX page pool counters and configuration.
- `hns3_dbg_bd_file_init()`, `hns3_dbg_common_init_t1()`, and `hns3_dbg_common_init_t2()` create debugfs files for local and backend-provided readers.
- `hns3_dbg_init()` creates the per-device debugfs tree and all supported files.
- `hns3_dbg_uninit()`, `hns3_dbg_register_debugfs()`, and `hns3_dbg_unregister_debugfs()` remove per-device and global debugfs trees.

## Control Flow

Module/global setup calls `hns3_dbg_register_debugfs()` to create the root. Device setup calls `hns3_dbg_init()`, which creates a per-PCI-device directory under the root, creates child directories, then iterates `hns3_dbg_cmd[]`. It skips unsupported TM nodes on old devices and PTP info when PTP capability is absent. Each command invokes its configured initializer: type 1 uses local seq-file readers, type 2 asks backend `dbg_get_read_func()` for a reader, and BD commands create one file per available queue. On any init error, the per-device tree is removed recursively.

Read flow for queue/page-pool/BD files resolves the handle from seq private data or `hns3_dbg_data`, checks ring/page-pool presence and reset/init state where needed, then reads software state and MMIO registers into seq output. Teardown removes debugfs recursively and clears saved dentries.

## State and Persistence Behavior

Debugfs dentries persist for the global module lifetime and per-device handle lifetime. Per-BD-file `hns3_dbg_data` arrays are `devm_kcalloc()` allocations tied to the PCI device. The file stores no durable state; it exposes live driver memory, live MMIO registers, cached capabilities/specs, descriptors, page pool counters, and DIM state. Reads can fail during reset to avoid dereferencing invalid ring memory.

## Dependencies and Integration Points

The module depends on Linux debugfs and seq_file APIs, `string_choices.h`, `hnae3.h`, `hns3_debugfs.h`, and `hns3_enet.h`. It integrates with NIC private structures (`hns3_nic_priv`, rings, vectors, descriptors, page pools), HNAE3 backend debug read functions, capability bits populated by command init, and queue/vector helpers from the NIC frontend.

## Risks and Edge Cases

- `hns3_dbg_dentry[]` is static global state reused per device; concurrent multi-device init could overwrite dentry pointers.
- Several read paths access live ring and descriptor memory; reset checks reduce but do not fully eliminate races without broader synchronization.
- BD dump files are created for max available channels, while reads reject queues beyond current `num_tqps`.
- `sprintf()` into `HNS3_DBG_FILE_NAME_LEN` relies on command names plus queue numbers fitting the 16-byte buffer.
- Backend `dbg_get_read_func()` failures abort all debugfs init for the device.
- Queue register reads assume mapped TQP MMIO remains valid during the seq read.

## Test Signals

Signals include debugfs tree creation/removal on probe/remove, all expected files under each directory, old-device and no-PTP skips, queue info reads during traffic, reset-time reads returning `-EPERM` or `-EBUSY` rather than crashing, BD dump bounds checks, page-pool absent behavior, backend-provided debug readers, and multi-device debugfs behavior.
