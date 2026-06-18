<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h

## Purpose
Defines the complete userspace ioctl ABI for UBI control devices, UBI character devices, and UBI volume devices. It covers MTD attach/detach, volume create/remove/resize/rename, volume update, LEB map/unmap/change/query, erase-counter reporting, volume properties, and read-only block device creation.

## Important APIs, Types, and Functions
Read coverage: 506 lines and 19854 bytes. Visible type families include struct ubi_set_vol_prop_req, struct ubi_attach_req, struct ubi_mkvol_req, struct ubi_rsvol_req, struct ubi_rnvol_req, struct ubi_ecinfo_req, struct ubi_leb_change_req, struct ubi_map_req, struct ubi_blkcreate_req. Important macros/constants include __UBI_USER_H__, UBI_VOL_NUM_AUTO, UBI_DEV_NUM_AUTO, UBI_MAX_VOLUME_NAME, UBI_IOC_MAGIC, UBI_IOCMKVOL, UBI_IOCRMVOL, UBI_IOCRSVOL, UBI_IOCRNVOL, UBI_IOCRPEB, UBI_IOCSPEB, UBI_IOCECNFO, UBI_CTRL_IOC_MAGIC, UBI_IOCATT, UBI_IOCDET, UBI_VOL_IOC_MAGIC, UBI_IOCVOLUP, UBI_IOCEBER, UBI_IOCEBCH, UBI_IOCEBMAP, UBI_IOCEBUNMAP, UBI_IOCEBISMAP, UBI_IOCSETVOLPROP, UBI_IOCVOLCRBLK, UBI_IOCVOLRMBLK, MAX_UBI_MTD_NAME_LEN, UBI_MAX_RNVOL, UBI_VOL_VALID_FLGS. Explicit ioctl-style command names include UBI_IOC_MAGIC, UBI_IOCMKVOL, UBI_IOCRMVOL, UBI_IOCRSVOL, UBI_IOCRNVOL, UBI_IOCRPEB, UBI_IOCSPEB, UBI_IOCECNFO, UBI_CTRL_IOC_MAGIC, UBI_IOCATT, UBI_IOCDET, UBI_VOL_IOC_MAGIC, UBI_IOCVOLUP, UBI_IOCEBER, UBI_IOCEBCH, UBI_IOCEBMAP, UBI_IOCEBUNMAP, UBI_IOCEBISMAP, UBI_IOCSETVOLPROP, UBI_IOCVOLCRBLK, UBI_IOCVOLRMBLK.

## Control Flow
Control-device flows attach an MTD device with `UBI_IOCATT` or detach with `UBI_IOCDET`. UBI device flows create, remove, resize, atomically rename, scrub, or query erase counters. Volume-device flows start an update by declaring byte count, write exactly that image, erase or atomically change LEBs, map/unmap/query LEB mappings, set properties such as direct-write, and create/remove UBI block devices.

## State and Persistence Behavior
The ABI mutates persistent UBI metadata on flash: device attachment records, volume tables, volume names and IDs, logical-to-physical eraseblock mappings, erase counters, update transactions, and volume flags such as skip-CRC-check. Some operations are transactional or asynchronous, such as unmap scheduling erase without waiting.

## Dependencies and Integration Points
It depends on Linux integer types and ioctl encoding. It integrates with MTD devices, UBI core, UBIFS, ubiblock, and userspace tools such as ubiattach, ubimkvol, ubirename, ubiupdatevol, and ubinfo. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Risks include fixed maximum name and rename counts, ABI-preserved 64-bit update-size encoding, asynchronous unmap persistence after power loss, atomic rename validation, autoresize semantics, and reserved padding that must remain zero/ignored for forward compatibility.

## Test Signals
Run UBI/UBIFS tests on nandsim, cover attach/detach, create/remove/resize/rename including atomic multi-volume rename, interrupted volume updates, LEB map/unmap/change across power-cut simulation, erase-counter queries, property setting, and ubiblock create/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/ubi-user.h -->
