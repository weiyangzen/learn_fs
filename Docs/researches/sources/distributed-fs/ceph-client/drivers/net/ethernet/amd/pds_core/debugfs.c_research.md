# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/debugfs.c

## Purpose
`debugfs.c` provides read-only debugfs observability for the AMD/Pensando core driver. It creates the module-level debugfs directory, per-device directories, identity and VIF-type files, queue/completion queue directories, and interrupt-control register dumps for AdminQ/NotifyQ-style QCQs.

## Important APIs, Types, And Functions
Public helpers are `pdsc_debugfs_create`, `pdsc_debugfs_destroy`, `pdsc_debugfs_add_dev`, `pdsc_debugfs_del_dev`, `pdsc_debugfs_add_ident`, `pdsc_debugfs_add_viftype`, `pdsc_debugfs_add_qcq`, and `pdsc_debugfs_del_qcq`. `identity_show` emits firmware heartbeat, identity counts, interrupt coalescing factors, and VIF-type words. `viftype_show` emits each named VIF type's support and enable state. `intr_ctrl_regs` names the interrupt-control register offsets exposed through `debugfs_create_regset32`.

## Control Flow
Module init calls `pdsc_debugfs_create`; module exit calls recursive destroy. Probe calls `pdsc_debugfs_add_dev` before deeper device init, creating a directory named by PCI device and a `state` file. Device identity discovery calls `pdsc_debugfs_add_ident`, which avoids duplicate creation during reset flows by checking for an existing `identity` file. Initial setup calls `pdsc_debugfs_add_viftype`. QCQ allocation calls `pdsc_debugfs_add_qcq`, creating top-level QCQ metadata, `q/`, `cq/`, and optional `intr/` subdirectories. Queue free and device remove remove the corresponding subtrees.

## State And Persistence
The only module-level state is `pdsc_dir`. Per-device and per-QCQ dentries are stored in `pdsc->dentry` and `qcq->dentry`. The files expose live kernel memory and MMIO register state read-only; there is no persistence beyond runtime debugfs entries.

## Dependencies And Integration Points
This file integrates with Linux debugfs, seq_file show helpers, PCI names, MMIO read helpers, devm allocation for register-set metadata, and shared driver state from `core.h`. It is called from module lifecycle, probe/remove, identity setup, VIF setup, and QCQ allocation/free.

## Risks
Debugfs files expose live data without taking driver locks, so output can be transient during reset or teardown. `pdsc_debugfs_add_ident` uses `debugfs_lookup` to avoid duplicates but does not explicitly drop the looked-up dentry, which is a pattern worth reviewing against current debugfs lookup semantics. `pdsc_debugfs_add_qcq` returns early on subdirectory allocation errors and can leave partial trees, though recursive removal later handles normal cleanup. Register-set memory is devm-managed while debugfs lifetime is tied to queue/device removal; teardown ordering must keep the device alive until debugfs entries are removed.

## Test Signals
Mount debugfs and verify per-device `state`, `identity`, `viftypes`, queue, CQ, and interrupt files after probe. Exercise firmware reset/recovery to ensure identity is not duplicated and stale QCQ directories disappear/reappear. Read files during traffic/AdminQ activity to verify counters and ring indices change without read faults.
