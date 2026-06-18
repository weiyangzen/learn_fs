# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-rpmb.c

## Purpose

`ufs-rpmb.c` registers UFS RPMB regions as Linux RPMB devices for OP-TEE style consumers when advanced RPMB is not used.

## Important APIs, Types, and Functions

Public functions are `ufs_rpmb_probe()` and `ufs_rpmb_remove()`. `struct ufs_rpmb_dev` binds a region id, device, `rpmb_dev`, HBA pointer, and list node. `ufs_sec_submit()` sends SECURITY PROTOCOL IN/OUT SCSI commands. `ufs_rpmb_route_frames()` implements the rpmb framework route callback.

## Control Flow

Probe skips registration without an RPMB WLUN or when advanced RPMB is enabled. It requires a device id, initializes `hba->rpmbs`, then registers one device per nonzero RPMB region capacity. Each region gets a unique id derived from UFS device id plus region number and an `rpmb_descr`. Route-frame requests validate frame sizes by RPMB request type, send request frames via SECURITY PROTOCOL OUT, optionally send a result-read request, then read the response via SECURITY PROTOCOL IN. Remove unregisters every listed region device.

## State and Persistence Behavior

State is runtime device/list registration and RPMB framework handles. Persistent data is inside the UFS RPMB hardware, not this driver. Request effects include key programming, counter reads, authenticated writes, and reads.

## Dependencies and Integration Points

It depends on SCSI WLUN commands, the Linux RPMB framework, UFS device info, and `ufshcd-priv.h` probe/remove hooks. It integrates secure storage clients with UFS RPMB regions.

## Risks and Test Signals

Risks include wrong frame-size validation, result-read sequencing errors, device-id absence, multi-region cleanup after partial registration failure, and using the non-advanced path when firmware expects advanced RPMB. Test signals include region registration counts, all RPMB request types, failed SECURITY PROTOCOL commands, partial-probe unwind, and remove with empty/nonempty lists.
