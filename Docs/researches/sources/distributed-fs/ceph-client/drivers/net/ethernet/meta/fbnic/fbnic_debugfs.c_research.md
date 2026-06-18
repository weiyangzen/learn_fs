# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_debugfs.c

## Purpose

`fbnic_debugfs.c` exposes FBNIC runtime diagnostics through debugfs. It renders queue descriptors, queue head/tail positions, programmed MAC/IP/action TCAM state, firmware mailbox descriptors, cached firmware logs, and PCIe outbound counters. The file is observational: it creates debugfs directories/files and formats current in-memory or CSR state through seq_file callbacks, with the only refresh side effect being explicit hardware stats collection for the PCIe stats file.

## Important APIs, Types, And Functions

Top-level lifecycle functions are `fbnic_dbg_init()` and `fbnic_dbg_exit()`, which create and remove the driver root named by `fbnic_driver_name`. Per-device functions `fbnic_dbg_fbd_init()` and `fbnic_dbg_fbd_exit()` create/remove files such as `pcie_stats`, `mac_addr`, `tce_tcam`, `act_tcam`, `ip_src`, `ip_dst`, `ipo_src`, `ipo_dst`, `fw_mbx`, and `fw_log`. Per-NAPI functions `fbnic_dbg_nv_init()` and `fbnic_dbg_nv_exit()` create `nv.%03d` subdirectories and ring descriptor files (`twq0`, `twq1`, `tcq`, `hpq`, `ppq`, `rcq`).

Descriptor output flows through `fbnic_dbg_desc_open()` and `fbnic_dbg_desc_fops`. It selects a show function from the ring doorbell offset: `fbnic_dbg_twq_desc_seq_show()`, `fbnic_dbg_tcq_desc_seq_show()`, `fbnic_dbg_bdq_desc_seq_show()`, or `fbnic_dbg_rcq_desc_seq_show()`. Decoders use CSR descriptor masks from `fbnic_csr.h` to print Tx work descriptors, Tx completion descriptors, Rx buffer descriptor IDs/addresses, and Rx completion metadata/action/timestamp/error fields.

Other show functions render classifier and firmware state: `fbnic_dbg_mac_addr_show()`, `fbnic_dbg_tce_tcam_show()`, `fbnic_dbg_act_tcam_show()`, `fbnic_dbg_ip_addr_show()` plus wrappers, `fbnic_dbg_fw_mbx_show()`, `fbnic_dbg_fw_log_show()`, and `fbnic_dbg_pcie_stats_show()`.

## Control Flow

Initialization is hierarchical. The module root is created once. Each device gets a PCI-name directory under that root. Each NAPI vector gets a subdirectory under the device directory, and the code walks the vector's Tx and Rx triads to derive hardware queue indices from `fbnic_ring_csr_base()` relative to `fbd->uc_addr0[FBNIC_QUEUE(0)]`.

When a ring file is read, `single_open()` stores the ring in `seq_file->private`. The show path first prints software ring metadata and reads hardware head/tail registers based on the ring doorbell offset. It then iterates the descriptor storage if allocated. If `ring->desc` is NULL, it reports that the ring is not allocated instead of dereferencing it.

Firmware mailbox output prints both Rx and Tx mailbox software readiness/head/tail and every raw mailbox descriptor read via `__fbnic_mbx_rd_desc()`. Firmware log output checks `fbnic_fw_log_ready()`, takes `fw_log.lock` with IRQ save, and walks entries in reverse list order to print newest-to-oldest cached messages. PCIe stats output takes RTNL, calls `fbnic_get_hw_stats()`, and prints selected `fbd->hw_stats.pcie` counters.

## State And Persistence

Debugfs dentries are kept in `fbnic_dbg_root`, `fbd->dbg_fbd`, and `nv->dbg_nv`. They are runtime-only and removed recursively during teardown. File contents are generated on read from current software state (`struct fbnic_ring`, `struct fbnic_dev`, TCAM arrays, mailbox state, firmware log buffer) and current hardware registers. Firmware log reads use the circular in-memory log buffer owned by `fbnic_fw_log.c`.

## Dependencies And Integration Points

The file depends on Linux debugfs, seq_file, PCI naming, RTNL, FBNIC ring helpers from `fbnic_txrx.h`, mailbox helpers from `fbnic_fw.c`, stats from `fbnic_hw_stats.c`, and classifier arrays maintained by MAC/RPC/RX mode code. It is integrated into device and NAPI lifecycle paths outside this file, which must call the init/exit helpers when devices and vectors appear or disappear.

## Risks And Edge Cases

Debugfs callbacks race with live device activity by design. Descriptor data can change while being printed; output should be treated as a snapshot best effort. The ring-doorbell switch assumes known FBNIC ring types; an unexpected doorbell offset returns `-EINVAL`. Firmware log display holds a spinlock while formatting each entry, so very large output could extend lock hold time. Device removal must call recursive debugfs removal before backing state is freed, or readers could access stale pointers. The PCIe stats file takes RTNL and reads hardware, so it has stronger side effects than the other views.

## Test Signals

Useful checks are debugfs tree creation/removal across probe/remove, reads of every ring file while rings are allocated and after they are freed, mailbox descriptor reads before and after firmware bringup, firmware log read returning `-ENXIO` before log init and formatted output after logs arrive, and `pcie_stats` values increasing after traffic. No executable tests were run for this research item.
