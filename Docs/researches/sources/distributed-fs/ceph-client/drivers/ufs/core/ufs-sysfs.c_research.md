# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-sysfs.c

## Purpose

`ufs-sysfs.c` exposes the UFS controller, link, device descriptor, unit descriptor, query flag, query attribute, monitor, write booster, PM, and host-initiated defrag controls through sysfs.

## Important APIs, Types, and Functions

Public functions are `ufs_sysfs_add_nodes()`, `ufs_sysfs_remove_nodes()`, and exported `ufshcd_us_to_ahit()`. Important helpers include `ufs_sysfs_pm_lvl_store()`, `ufshcd_read_hci_reg()`, `ufs_sysfs_read_desc_param()`, `hid_query_attr()`, descriptor/flag/attribute macros, and visibility callbacks for HID and unit descriptors. It exports `ufs_sysfs_unit_descriptor_group` and `ufs_sysfs_lun_attributes_group` for SCSI device attachment.

## Control Flow

Host sysfs group creation installs default controls, capabilities, UFSHCI registers, monitor counters, power info, device/interconnect/geometry/health/power/string descriptors, flags, attributes, and HID controls. Device-affecting reads/writes generally take `host_sem`, check `ufshcd_is_user_access_allowed()`, resume runtime PM, issue UFS query or register access, then release PM and semaphore. PM level writes validate allowed levels and deep-sleep capability. Write booster and buffer flush writes validate feature/quirk support and update UFS flags or attributes. Descriptor macros read fixed-size big-endian fields; string descriptors first read the device descriptor to find string indexes. LUN groups convert SCSI LUNs to UPIU LUNs and hide unsupported WLUN attributes.

## State and Persistence Behavior

Sysfs writes mutate live HBA fields (`rpm_lvl`, `spm_lvl`, monitor state, RTC update period, PM QoS state, WB flush threshold, counters) and device attributes/flags. Some effects persist in the UFS device until reset or later query writes, but this file itself stores no on-disk state. Monitor counters live in `hba->monitor`; exception counters are atomic HBA fields.

## Dependencies and Integration Points

It depends on sysfs, SCSI device objects, runtime PM on the device WLUN, UFS query descriptor/flag/attribute helpers, UFSHCI registers, write booster helpers, PM QoS, clock scaling, HID attributes, and unit descriptor LUN validation in `ufshcd-priv.h`.

## Risks and Test Signals

Risks include ABI regressions, missing access gating around device queries, descriptor offset/size mismatches, endian conversion mistakes, runtime-PM failures, monitor reset races under `host_lock`, queue freeze ordering for max RTT writes, and visibility errors for WLUNs/HID support. Test signals include sysfs group create/remove, every descriptor family on real or emulated devices, WB enable/flush/resize controls, auto-hibern8 conversion round trips, PM level validation, HID enable/disable/progress reads, LUN descriptor visibility, and shutdown returning `-EBUSY`.
