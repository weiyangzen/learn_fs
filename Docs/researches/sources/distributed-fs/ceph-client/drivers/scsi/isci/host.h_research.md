# sources/distributed-fs/ceph-client/drivers/scsi/isci/host.h

## Purpose

`host.h` declares the controller object model and public controller-side APIs for the `isci` driver. It ties together libsas host state, SCU/SMU register windows, DMA context tables, phy/port/device arrays, power control, port configuration, wait queues, tasklets, and the common SCI state machine.

## Important APIs, Types, and Functions

`struct isci_host` is the primary type. It contains `sci_base_state_machine sm`, user and OEM parameters, `sci_port_configuration_agent`, `device_table`, `sci_remote_node_table`, `sci_power_control`, IO sequence numbers, task/RNC/completion/UFI DMA memory, unsolicited-frame control, phy-start timers, interrupt coalescing fields, MMIO register pointers, TCI circular pool, controller ID, `phys[]`, `ports[]`, `sas_ports[]`, `sas_ha`, PCI device, flags, event waitqueue, completion tasklet, lock, request table, and remote-device storage.

`struct sci_power_control` tracks SATA/SAS spin-up throttling with a timer, `phys_waiting`, `phys_granted_power`, and per-phy requester slots. `struct sci_port_configuration_agent` tracks configured and ready phy masks, valid port ranges, a timer, and link-up/link-down handler callbacks. `enum sci_controller_states` defines controller lifecycle states from initial/reset/initializing/initialized through starting/ready/resetting/stopping/failed.

Inline helpers include `to_pci_info()`, `to_shost()`, `for_each_isci_host`, wait helpers for host/device start and stop, `dev_to_ihost()`, `idev_to_ihost()`, tag construction/extraction macros `ISCI_TAG`, `ISCI_TAG_SEQ`, `ISCI_TAG_TCI`, revision helpers `is_a2()` through `is_c1()`, cable override helpers, and `isci_gpio_count()`. External declarations expose controller posting, frame release/copy, RNC allocation/free, request lookup, power-control queue operations, link notifications, IO/task lifecycle, host init/deinit/start/completion, port-configuration agent operations, and GPIO writes.

## Control Flow

The header defines the state transitions that `host.c` implements. Probe allocates `struct isci_host`, initializes ports/phys/devices, and calls `isci_host_init()`. Scanning invokes `isci_host_start()`, and `isci_host_scan_finished()` blocks SCSI scan completion until the start flag clears. IO paths allocate tags, start requests or tasks, complete or terminate them, and free tags through the declared controller APIs. Link notifications from `phy.c` enter `sci_controller_link_up()` or `sci_controller_link_down()`, which dispatch to the port-configuration agent. Remove/suspend paths call `isci_host_deinit()` and wait helpers.

## State and Persistence Behavior

`host.h` defines all controller runtime state but no persistent storage. Flags `IHOST_START_PENDING`, `IHOST_STOP_PENDING`, and `IHOST_IRQ_ENABLED` coordinate async lifecycle and interrupt masking. The device table maps hardware remote-node indexes to `isci_remote_device` objects, while the TCI pool and IO sequence array protect request reuse. OEM/user parameters are stored per host after module/platform/firmware parsing, and cable selections may be overridden globally through the module parameter declared elsewhere.

## Dependencies and Integration Points

The header includes libsas/SATA integration (`scsi/sas_ata.h`), remote device, phy, remote-node table, registers, unsolicited frame control, and probe ROM parameter definitions. It is included by most `isci` source files to share controller state and exported controller operations. It also binds to PCI through `struct pci_dev`, to SCSI through `Scsi_Host`, and to libsas through `sas_ha_struct`, `asd_sas_port`, and `asd_sas_phy`.

## Risks and Edge Cases

Because `struct isci_host` embeds arrays sized by hardware constants, changing `SCI_MAX_*` constants affects DMA table sizing, pool masks, tag encoding, and object lifetimes across the driver. `ISCI_TAG_SEQ()` and `ISCI_TAG_TCI()` assume power-of-two sequence and request counts, enforced in `isci.h`; mismatches would make stale completion checks unsafe. The wait helpers rely on flags being cleared on every failure and timeout path. `ports[SCI_MAX_PORTS + 1]` includes a dummy port, so callers must avoid treating every entry as a real libsas port.

## Test Signals

Compile-time signals include all users agreeing on `struct isci_host` field names and exported prototypes. Runtime signals include waiters waking on host/device start/stop, correct tag reuse behavior after many request cycles, link-up/down routing through the configured port mode, and remove/suspend paths deleting timers without use-after-free.
