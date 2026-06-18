# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.c

Purpose: Exposes lightweight debugfs diagnostics for HNS RoCE, currently software DFX counters per device.

Important APIs/types/functions: `hns_roce_init_debugfs()` creates the module root `hns_roce`; `hns_roce_cleanup_debugfs()` removes it. `hns_roce_register_debugfs()` creates a device directory named by PCI device and a `sw_stat/sw_stat` seqfile. `hns_roce_unregister_debugfs()` removes the device tree. `sw_stat_debugfs_show()` prints all software DFX counters.

Control flow: Registration builds nested debugfs dentries and initializes a seqfile wrapper whose open method calls `single_open()` with the stored read function and data pointer. Reads iterate `HNS_ROCE_DFX_CNT_TOTAL` and print names plus atomic64 counter values.

State and persistence: Global root dentry persists for module lifetime. Per-device dentries persist between device register/unregister. Counter values live in `hr_dev->dfx_cnt`.

Dependencies and integration: Depends on Linux debugfs, seq_file, PCI naming, and the DFX counter enum in `hns_roce_device.h`. AH, CQ, command, MR, QP, SRQ, mmap, and ucontext paths increment these counters.

Risks: Debugfs creation failures are ignored, which is typical but means diagnostics may be absent without hard failure. The counter-name array must stay aligned with the enum. Test signals include debugfs mount/read checks, device hotplug removal, counter increment visibility after induced errors, and enum/name coverage when new counters are added.
