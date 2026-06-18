# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.c

## Purpose

This file implements the hardware mapping and ioctl handling for Intel Speed Select Technology over TPMI. It hides package, partition, and power-domain layout details from userspace while exposing the same `/dev/isst_interface` UAPI used by older ISST transports.

## Important APIs, Types, And Functions

Core state types are `struct tpmi_per_power_domain_info`, `struct tpmi_sst_struct`, and `struct tpmi_sst_common_struct`. Discovery helpers include `sst_main()`, `sst_add_perf_profiles()`, `map_partition_power_domain_id()`, and `get_instance()`. Ioctl handlers cover core power (`isst_if_core_power_state()`), CLOS params/association, performance levels and feature state, level data, fabric data, CPU masks, base frequency, TPMI instance count, and turbo frequency. Public exported core functions are `tpmi_sst_init()`, `tpmi_sst_exit()`, `tpmi_sst_dev_add()`, `tpmi_sst_dev_remove()`, `tpmi_sst_dev_suspend()`, and `tpmi_sst_dev_resume()`.

## Control Flow

`tpmi_sst_init()` allocates the global package array and registers a TPMI backend default ioctl callback with the common ISST layer. `tpmi_sst_dev_add()` checks firmware read/write block status, gets OOB platform data, validates package and partition, maps each TPMI SST resource, parses SST/CP/PP headers, builds per-level offsets, and installs the partition into the package instance. `isst_if_def_ioctl()` serializes all TPMI ioctls under `isst_tpmi_dev_lock` and dispatches based on UAPI command. Removal clears the partition and frees the package instance when all partitions are gone. Suspend stores CP control, CLOS config/association, and PP control; resume writes them back.

## State And Persistence

Global state is `isst_common.sst_inst`, `isst_core_usage_count`, and package instances protected by `isst_tpmi_dev_lock`. Per-power-domain state includes mapped MMIO, header snapshots, level mappings, saved suspend values, write-block status, and device pointers. The driver preserves selected controls across suspend/resume but not reboot.

## Dependencies And Integration Points

The file depends on Intel TPMI resource APIs, Intel VSEC/OOB platform data, common ISST char-device registration, x86 HWP/MSR checks, topology package counts, and TPMI power-domain namespace imports. It translates UAPI structs from `uapi/linux/isst_if.h` into TPMI register reads/writes.

## Risks

Partition mapping is complex: if one partition is unbound, `map_partition_power_domain_id()` rejects all mappings because `partition_mask_current` no longer matches `partition_mask`. Several static local UAPI buffers are used in read handlers, but the global ioctl lock serializes access. Dynamic writes are blocked when HWP is unavailable or disabled. A likely bug exists in resume: the PP restore writes to `power_domain_info->sst_base` rather than `pd_info->sst_base`, which would restore all PP controls through the first element's base. Register-field macros must track TPMI spec revisions exactly.

## Test Signals

Tests should verify package/partition enumeration, instance count valid masks, invalid partition unbind behavior, all read-only info ioctls, CAP_SYS_ADMIN and write-block enforcement, dynamic feature rejection when HWP is off, level switching and retry behavior, CLOS association mapping, suspend/resume restore, and multi-resource systems with compute and IO dies.
