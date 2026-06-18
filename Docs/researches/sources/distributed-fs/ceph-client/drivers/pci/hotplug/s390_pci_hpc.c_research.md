# sources/distributed-fs/ceph-client/drivers/pci/hotplug/s390_pci_hpc.c

## Purpose
Implements PCI hotplug slot operations for IBM Z `zpci` functions. It maps generic PCI hotplug actions to s390 configure, deconfigure, reset, and status operations.

## Important APIs, Types, and Functions
Public functions are `zpci_init_slot()` and `zpci_exit_slot()`. Hotplug callbacks are `enable_slot()`, `disable_slot()`, `reset_slot()`, `get_power_status()`, and `get_adapter_status()` in `s390_hotplug_slot_ops`.

## Control Flow
Enabling requires the zPCI function to be in `STANDBY`, calls `sclp_pci_configure()`, marks it configured, and scans the configured device. Disabling requires `CONFIGURED`, rejects PFs with enabled VFs by checking `pci_num_vf()`, then calls `zpci_deconfigure_device()`. Reset uses `mutex_trylock()` to avoid waiting during state transitions, supports probe queries, and calls `zpci_hot_reset_device()` only for configured functions. Registration names the hotplug slot by FID.

## State and Persistence Behavior
State is held in `struct zpci_dev`: function state, FID/FH, devfn, zbus, state lock, and embedded hotplug slot. Firmware/hardware configured state changes through SCLP and zPCI reset/deconfigure calls.

## Dependencies and Integration Points
Depends on s390 SCLP PCI configure, zPCI scan/deconfigure/reset helpers, PCI hotplug core, zPCI debug, and SR-IOV helper `pci_num_vf()`.

## Risks
State transitions are serialized by `zdev->state_lock`; reset intentionally fails if the lock is busy. Disabling a PF with active VFs returns `-EBUSY`, so callers must quiesce SR-IOV first. Adapter status always reports present because a zPCI slot represents an existing function.

## Test Signals
Configure/deconfigure a standby/configured function, reset configured and unconfigured functions, disable PFs with and without VFs, hotplug slot registration naming, concurrent state transitions, and power/adapter sysfs reads.
