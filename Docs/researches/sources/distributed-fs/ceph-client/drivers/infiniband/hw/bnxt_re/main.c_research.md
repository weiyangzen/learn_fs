# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/main.c

## Purpose
`main.c` is the top-level Linux RDMA driver glue for Broadcom NetXtreme-E RoCE. It binds as a `bnxt_en` auxiliary driver, negotiates capabilities with the Ethernet function through HWRM and ULP callbacks, creates the qplib firmware/control channel, allocates interrupt and queue resources, registers an `ib_device`, and tears everything down on remove, recovery suspend, resume, or shutdown.

## Important APIs, types, and functions
The file centers on `struct bnxt_re_dev`, `struct bnxt_re_en_dev_info`, `struct bnxt_ulp_ops`, `struct auxiliary_driver`, and the static `ib_device_ops` tables. Setup helpers include `bnxt_re_setup_chip_ctx()`, `bnxt_re_set_drv_mode()`, `bnxt_re_set_db_offset()`, `bnxt_re_dev_init()`, `bnxt_re_alloc_res()`, `bnxt_re_init_res()`, and `bnxt_re_register_ib()`. HWRM helpers allocate/configure VNICs, rings, stats contexts, firmware version, function config, function caps, and doorbell pacing config. Runtime and recovery hooks are `bnxt_re_stop_irq()`, `bnxt_re_start_irq()`, `bnxt_re_suspend()`, `bnxt_re_resume()`, and `bnxt_re_remove_device()`. Async handlers translate CREQ/QP/CQ errors into IB events and update QP1 ToS/DSCP after DCB changes.

## Control flow
Module init registers debugfs and the auxiliary driver. Probe allocates `bnxt_re_en_dev_info`, creates `bnxt_re_dev`, registers with the Ethernet driver, validates MSI-X count, builds chip context, maps the doorbell BAR, allocates RCFW CMDQ/CREQ, allocates a CREQ firmware ring, enables RCFW interrupts, optionally initializes DBR pacing, queries device attributes and firmware version, allocates qplib resources, allocates NQs and their firmware rings, initializes NQs, configures VF resource limits for PFs, creates debugfs/DCB workqueue registration, reads VPD for PFs, and finally registers the RDMA device. Remove and suspend reverse the same layers through flag-guarded cleanup so partially initialized devices can unwind.

## State and persistence
Driver state is in RAM: `rdev->flags`, `chip_ctx`, `qplib_res`, `qplib_ctx`, `rcfw`, NQ ring state, stats DMA contexts, DCB workqueue, pacing page, CQ/SRQ hashes, QP list, and board VPD cache. Persistent device state is only what firmware owns after HWRM/RCFW commands: rings, stats contexts, context tables, pacing config, resource limits, VNIC state, and RoCE CC state. Pacing also exposes a shared page to user processes through `qplib_res.pacing_data`.

## Dependencies and integration points
The file integrates the RDMA core, auxiliary bus, PCI, `bnxt_en` ULP API, HWRM firmware mailbox, qplib resource/slow/fast-path modules, netdevice carrier state, DCB async events, debugfs, rdma restrack, VPD, and Linux PM/recovery callbacks. Most IB verbs are implemented in `ib_verbs.c` but registered here via `bnxt_re_dev_ops`.

## Risks
Initialization has many cross-driver resources, so failure ordering is critical. The source snapshot contains duplicated `if (BNXT_EN_VF(...))` in `bnxt_re_get_sriov_func_type()`, which may indicate merge damage. `bnxt_re_dev_init()` calls `bnxt_re_dev_uninit()` on broad failure paths after some labels have already freed pieces, so flag state must remain accurate. DBR pacing reads MMIO and uses workqueue/timer locking; missed cancellation can race teardown. Async QP/CQ error translation dereferences handles supplied by firmware and depends on qplib hash/table correctness. Suspend assumes `en_info->rdev` is valid before locking. `bnxt_re_shutdown()` does not clear `en_info->rdev`.

## Test signals
Build with `CONFIG_INFINIBAND_BNXT_RE`, auxiliary bus, PCI, and bnxt_en. Exercise probe/remove, insufficient MSI-X, HWRM query failures, RCFW channel failure, NQ ring failure, DBR pacing unsupported/failure paths, PF and VF resource limits, DCB config change, firmware fatal suspend, recovery resume, RDMA registration, restrack raw context reads, and carrier-up/down initial port event selection.
