# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.c

## Purpose

This file implements the common Intel Speed Select userspace interface. It creates `/dev/isst_interface`, tracks registered backend callbacks, validates and dispatches ioctls, maps logical CPUs to P-unit/PCI topology, and stores selected write commands for replay after resume.

## Important APIs, Types, And Functions

Exports include `isst_if_cdev_register()`, `isst_if_cdev_unregister()`, `isst_if_get_pci_dev()`, `isst_if_mbox_cmd_invalid()`, `isst_if_mbox_cmd_set_req()`, `isst_store_cmd()`, and `isst_resume_common()`. Internal state includes `punit_callbacks[]`, `isst_cpu_info`, `isst_pkg_info`, and the `isst_hash` command replay table. `isst_if_def_ioctl()` handles platform info, CPU map, MMIO, mailbox, MSR, and backend default ioctls. `isst_if_exec_multi_cmd()` handles batched user commands with a maximum of 64.

## Control Flow

Module init checks CPU model support. For legacy mailbox-only Skylake-X it verifies OS mailbox MSRs; for HPM platforms it blocks legacy non-TPMI backends. It initializes CPU topology via a dynamic CPU hotplug state and registers the misc device. Backends register callbacks for MBOX, MMIO, or TPMI. On open, module refs are taken for registered backends; ioctl dispatch copies each command from userspace, invokes the registered callback, and copies results back unless the callback marks it write-only. Resume replay iterates stored writes and reissues mailbox or MSR writes.

## State And Persistence

State is in global callback slots, CPU/package topology caches, misc-device open count, API version, and replay hash. Replay state persists only in memory across suspend/resume, not reboot. The open lock prevents backend registration changes while userspace has the device open.

## Dependencies And Integration Points

The file integrates with `uapi/linux/isst_if.h`, x86 CPU matching, cpuhotplug, PCI enumeration, MSR access, miscdevice, module references, and backend modules. It uses MSR `0x128`, `MSR_THREAD_ID_INFO`, and `MSR_PM_LOGICAL_ID` for topology.

## Risks

The shared global callback slots mean multiple devices of the same backend type can conflict; registration fails if the device is open but replacement behavior otherwise is coarse. Topology mapping depends on NUMA and PCI bus numbering heuristics. Only whitelisted mailbox and MSR commands are allowed; stale whitelists can block new features or allow unsafe ones. `isst_if_relase` is misspelled but wired correctly as `.release`.

## Test Signals

Test `/dev/isst_interface` creation, `ISST_IF_GET_PLATFORM_INFO`, batched command limits, logical-to-P-unit CPU mapping, invalid command rejection, CAP_SYS_ADMIN enforcement for writes, backend registration/unregistration while open, suspend/resume replay, and unsupported CPU model `-ENODEV`.
