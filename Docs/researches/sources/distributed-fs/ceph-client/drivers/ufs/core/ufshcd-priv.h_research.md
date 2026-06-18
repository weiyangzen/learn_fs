# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-priv.h

## Purpose

`ufshcd-priv.h` is the private contract between the UFS core implementation files. It declares core helpers, optional subsystem hooks, variant-operation wrappers, runtime PM helpers, exception-event mask helpers, LUN conversion, and MCQ queue inline operations.

## Important APIs, Types, and Functions

The header declares UFS query helpers, MCQ APIs, BSG/raw UPIU helpers, write booster helpers, TXEQ APIs, RPMB hooks, and error/command-control helpers. `enum ufs_descr_fmt` defines raw versus ASCII string descriptor reads. Important inline wrappers cover variant ops such as clock scaling, link startup, power changes, MCQ resource configuration, RX FOM, TXEQTR settings, suspend/resume, and debug register dumps. Runtime PM helpers operate on `hba->ufs_device_wlun->sdev_gendev`.

## Control Flow

Most logic is small dispatch: if a variant op exists, call it; otherwise return neutral success or `-EOPNOTSUPP` depending on whether the operation is optional or required. MCQ inline helpers update SQ/CQ head and tail slots and convert queue register byte offsets to slots. Exception-event mask helpers merge driver and user masks through `ufshcd_update_ee_control()`.

## State and Persistence Behavior

The header does not allocate state but reads/mutates HBA fields through inline helpers: write booster LUN index, runtime PM refs, MCQ queue slots, exception masks, and shutdown/user-access state. Effects are runtime-only and often reflect hardware register state.

## Dependencies and Integration Points

It depends on PM runtime, UFS public headers, SCSI/block-mq request tags, optional hwmon/RPMB configs, variant ops, and almost every UFS core `.c` file. It is the main coupling layer between `ufshcd.c`, sysfs, debugfs, MCQ, TXEQ, BSG, crypto, hwmon, and RPMB code.

## Risks and Test Signals

Risks include inline semantics changing many call sites, returning `-EOPNOTSUPP` where callers expect success, runtime PM helper use before WLUN exists, tag-to-command lookup warnings during races, MCQ slot math mismatches with hardware entry sizes, and LUN validation before `max_lu_supported` initialization. Test signals include build coverage across optional configs, variant-op absent/present behavior, runtime PM balancing, MCQ completion slot updates, exception mask merging, and valid/invalid unit descriptor LUNs.
