# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.c

## Purpose

`amd_sfh_pcie.c` is the PCI transport driver for AMD MP2/SFH. It binds PCI IDs, maps MMIO registers, selects legacy or v2 command operations, handles interrupts, exposes HPD sysfs control for SFH 1.1, schedules initialization work, and wires runtime power-management callbacks.

## Important APIs, Types, and Functions

The module defines PCI driver `pcie_mp2_amd`. Legacy/v2 command helpers include `amd_start_sensor()`, `amd_stop_sensor()`, `amd_stop_all_sensors()`, `amd_start_sensor_v2()`, `amd_stop_sensor_v2()`, `amd_stop_all_sensor_v2()`, and `amd_sfh_wait_response_v2()`. `amd_mp2_get_sensor_num()` converts active sensor masks into sensor IDs, with DMI and module-parameter overrides. `mp2_select_ops()` installs legacy or v2 `amd_mp2_ops`. Probe/remove/shutdown/PM paths are `amd_mp2_pci_probe()`, `amd_sfh_remove()`, `amd_sfh_shutdown()`, `amd_mp2_pci_suspend()`, and `amd_mp2_pci_resume()`.

## Control Flow

Probe rejects known unsupported Google systems, applies DMI interrupt quirks, allocates `amd_mp2_dev`, enables PCI, maps BAR 2, sets DMA mask, allocates client data, initializes the mutex, and checks whether the PCI ID carries SFH 1.1 ops. SFH 1.1 devices schedule `sfh1_1_init_work()`. Legacy devices select ops, initialize interrupts if supported, and schedule `sfh_init_work()`, which calls `amd_sfh_hid_client_init()`. Remove and shutdown flush work before stopping sensors.

## State and Persistence Behavior

Persistent state is stored in `amd_mp2_dev` and PCI driver data. Module state includes `sensor_mask_override` and `intr_disable`, both affecting runtime discovery/commands. Sysfs attribute `hpd` reflects and toggles `mp2->dev_en.is_hpd_enabled` through SFH 1.1 ops.

## Dependencies and Integration Points

The driver depends on PCI managed resources, DMA, DMI matching, interrupts, MMIO polling, workqueues, and HID client code. It integrates with `sfh1_1/amd_sfh_init.c` through `sfh1_1_ops` for `PCI_DEVICE_ID_AMD_MP2_1_1`.

## Risks and Test Signals

Risks include DMI overrides hiding real sensors, long 10-second response polling during probe, interrupt quirks changing firmware behavior, and cleanup differences between legacy and SFH 1.1 paths. Test signals are PCI probe on both IDs, sensor mask module parameter behavior, sysfs HPD visibility only when present, suspend/resume, shutdown stop-all, and no IRQ storms after `amd_sfh_clear_intr()`.
