# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_pci.c

## Purpose

This backend implements Speed Select P-unit mailbox commands through PCI config-space registers on CFG mailbox devices.

## Important APIs, Types, And Functions

`struct isst_if_device` holds a per-PCI-device mutex. `isst_if_mbox_cmd()` polls the mailbox busy bit, writes request data and command fields to PCI config offsets `0xA0` and `0xA4`, then polls completion and reads response data. `isst_if_mbox_proc_cmd()` validates the user command, locates the PCI device for the target CPU via `isst_if_get_pci_dev(cpu, 1, 30, 1)`, serializes with the device mutex, and stores set commands for resume.

## Control Flow

The PCI driver matches Intel CFG mailbox device IDs. Probe enables the device, allocates state, registers the MBOX callback, and remove unregisters it. Runtime ioctls flow through common code into `isst_if_mbox_proc_cmd()`. Device PM resume calls `isst_resume_common()`.

## State And Persistence

Per-device state is just a mutex in PCI drvdata. Common replay state persists writes across suspend. Hardware config-space mailbox state is transient.

## Dependencies And Integration Points

It integrates with PCI probe/remove/PM, common ISST topology mapping, common ioctl dispatch, command validation, and CAP_SYS_ADMIN policy.

## Risks

Only one global MBOX callback slot exists, so multi-device registration is coarse even though each PCI device has its own mutex. Mailbox polling uses a one-millisecond max timeout with rescheduling after typical latency; long firmware stalls can produce `-EBUSY`. Correct CPU-to-PCI mapping is critical.

## Test Signals

PCI ID probe, `/dev/isst_interface` MBOX support, valid command response, invalid command rejection, set-command privilege and replay, suspend/resume replay, and timeout paths are the main signals.
