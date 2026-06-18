# sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.c

## Purpose
`mptctl.c` implements `/dev/mptctl`, the misc-device ioctl interface for Fusion MPT controllers. It exposes adapter information, target inventory, event reporting, diagnostic reset, firmware download/replacement, HP compatibility queries, and controlled raw MPI command pass-through to user space.

## Important APIs, Types, and Functions
The file registers `mptctl_fops` and `mptctl_miscdev`, with `mptctl_ioctl()` and optional `compat_mpctl_ioctl()` as user entry points. Command dispatch is in `__mptctl_ioctl()`. Completion paths are `mptctl_reply()` and `mptctl_taskmgmt_reply()`. Major handlers include `mptctl_fw_download()`, `mptctl_do_fw_download()`, `mptctl_mpt_command()`, `mptctl_do_mpt_command()`, `mptctl_do_reset()`, `mptctl_getiocinfo()`, `mptctl_gettargetinfo()`, `mptctl_readtest()`, `mptctl_eventquery()`, `mptctl_eventenable()`, `mptctl_eventreport()`, `mptctl_replace_fw()`, `mptctl_hp_hostinfo()`, and `mptctl_hp_targetinfo()`. DMA helper routines are `kbuf_alloc_2_sgl()` and `kfree_sgl()`.

## Control Flow
Module init registers a base-driver device callback, the misc device, the main and task-management completion callbacks, plus reset and event handlers. An ioctl copies the common header from user space, verifies the target adapter, handles read-only/status commands immediately, and serializes interrupt-dependent commands through `ioc->ioctl_cmds.mutex`. Raw MPI pass-through obtains a request frame, preserves the driver message context, copies the user message, validates allowed MPI functions, appends up to one outbound and one inbound SGE, posts the frame, waits for completion, then copies reply, sense, and inbound data back to user space. Timeouts invoke task management for SCSI-like requests and may escalate to a soft/hard reset.

## State and Persistence
The driver uses global registration IDs (`mptctl_id`, `mptctl_taskmgmt_id`), a global ioctl mutex, a wait queue, and an async SIGIO queue. Per-adapter state lives in `MPT_ADAPTER`: `ioctl_cmds`, `taskmgmt_cmds`, event log buffers, cached firmware, reset counters, and SCSI host/target data. Firmware replacement updates the in-memory cached firmware image and IOC facts; event enable allocates an in-memory circular-style event array. No user data persists across driver unload except firmware state resident in the controller.

## Dependencies and Integration Points
The file integrates with the miscdevice subsystem, Linux compat ioctl handling, user-copy APIs, PCI DMA allocation/mapping, SCSI mid-layer device lists, fasync/SIGIO, and Fusion base callbacks. It relies on MPI request/reply structures from the LSI headers and on `mptbase` functions for adapter lookup, config access, frame posting, firmware memory, reset, and task management.

## Risks and Edge Cases
This is a privileged raw hardware control surface. The command path must reject unsafe MPI functions, frame-size overflows, negative sizes, out-of-range bus/target IDs, and IOC_INIT mismatches. It still trusts many user-provided request fields after validation. Firmware download allocates DMA buffers in chunks and refuses chain SGE requirements; large images can fail with `-EMLINK` or memory pressure. Timeout recovery races with IOC reset and completion state. Compat paths must preserve pointer-width semantics. Event signaling uses a single global async queue and per-IOC `aen_event_read_flag`, so multi-consumer semantics are weak.

## Test Signals
Test coverage should include ioctl ABI size checks for all `MPTIOCINFO` revisions and compat structs, invalid adapter and inactive-controller paths, raw command rejection for illegal MPI functions, SCSI pass-through with sense data, timeout injection, firmware download with boundary-sized images, event enable/report plus SIGIO, HP host/target info queries, and reset during an outstanding ioctl.
