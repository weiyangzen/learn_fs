# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_sriov.c

## Purpose

`nitrox_sriov.c` manages Nitrox PF transitions between normal PF crypto mode and SR-IOV mode. It validates VF counts, maps VF counts to hardware modes and queue allocation, disables PF crypto resources before VF enablement, initializes SR-IOV interrupts/mailbox support, configures hardware VF mode, and restores PF queues/crypto registration when SR-IOV is disabled.

## Important APIs, Types, And Functions

- `num_vfs_valid()` allows only 16, 32, 64, or 128 VFs.
- `num_vfs_to_mode()` maps 0/16/32/64/128 to `__NDEV_MODE_PF`, `__NDEV_MODE_VF16`, `__NDEV_MODE_VF32`, `__NDEV_MODE_VF64`, or `__NDEV_MODE_VF128`.
- `vf_mode_to_nr_queues()` maps PF mode to 64 queues and VF modes to 8/4/2/1 queue per VF.
- `nitrox_pf_cleanup()` marks PF not ready, unregisters crypto algorithms, interrupts, and common PF resources.
- `nitrox_pf_reinit()` reallocates PF resources, registers interrupts, configures AQM and packet rings/ports, marks ready, and re-registers crypto algorithms.
- `nitrox_sriov_init()`/`nitrox_sriov_cleanup()` manage SR-IOV PF interrupts and mailbox state.
- `nitrox_sriov_enable()` and `nitrox_sriov_disable()` implement the PCI SR-IOV callbacks.
- `nitrox_sriov_configure()` dispatches enable or disable based on `num_vfs`.

## Control Flow

Enabling checks VF count validity and returns early if already configured to that exact count. It calls `pci_enable_sriov()`, stores the mode, VF count, and per-VF queue count, sets the SR-IOV flag, then calls `nitrox_pf_cleanup()` because the PF has no queues in SR-IOV mode. It registers PF SR-IOV interrupts and mailbox support, then writes the NPS core VF configuration mode. If mailbox/interrupt init fails, it disables PCI SR-IOV, clears flags/counts/mode, and attempts `nitrox_pf_reinit()`.

Disabling first checks the SR-IOV flag. If VFs are assigned to VMs, it refuses with `-EPERM`. Otherwise it disables PCI SR-IOV, clears flags and VF queue state, returns to PF mode, cleans up SR-IOV mailbox/interrupt resources, writes PF hardware mode, and reinitializes PF crypto resources.

## State And Persistence Behavior

The driver mutates `ndev->mode`, `ndev->iov.num_vfs`, `ndev->iov.max_vf_queues`, `ndev->flags`, and `ndev->state`. Hardware state changes through PCI SR-IOV enable/disable and `config_nps_core_vfcfg_mode()`. PF Crypto API availability is deliberately removed during SR-IOV mode and restored on disable.

## Dependencies And Integration Points

This file depends on Linux PCI SR-IOV APIs, Nitrox HAL configuration, common queue/interrupt setup, crypto algorithm registration, SR-IOV interrupt registration, and mailbox functions from `nitrox_mbx.h`. It is wired into the PCI driver through `.sriov_configure` in `nitrox_main.c`.

## Risks And Edge Cases

- If `nitrox_pf_reinit()` fails during rollback or disable, the PF may remain not ready after SR-IOV teardown.
- Enabling only supports fixed VF counts; arbitrary counts are rejected even if PCI core would permit them.
- PF cleanup unregisters crypto algorithms globally; multi-device behavior depends on the broader Nitrox crypto registration layer tolerating repeated unregister/register.
- `pci_vfs_assigned()` prevents disabling assigned VFs, but callers must surface `-EPERM` properly to administrators.

## Test Signals

Signals include sysfs SR-IOV enable for 16/32/64/128 VFs, rejection for unsupported counts, VF mailbox functionality, PF algorithms disappearing during SR-IOV and returning after disable, refusal while VFs are assigned, hardware VF mode register changes, and rollback from simulated interrupt/mailbox init failure.
