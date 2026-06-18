# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.h

## Purpose
`core.h` is the private header for the AMD/Pensando core driver. It defines driver constants, central runtime structures, queue and completion abstractions, interrupt tracking, VIF-type bookkeeping, state flags, doorbell encoding helpers, and prototypes shared across the driver's implementation files.

## Important APIs, Types, And Functions
Important structures include `pdsc_dev_bar` for PCI BAR metadata, `pdsc_vf` for per-VF auxiliary-device state, `pdsc_devinfo` for firmware/device strings, `pdsc_queue` for submission queues, `pdsc_intr_info` for MSI-X vectors, `pdsc_q_info`/`pdsc_cq_info`/`pdsc_buf_info` for descriptor software metadata, `pdsc_cq` for completion queues, `pdsc_qcq` for queue/completion/interrupt bundles, `pdsc_viftype` for supported runtime service types, and `pdsc` as the device-private root.

`enum pdsc_state_flags` defines `PDSC_S_FW_DEAD`, `PDSC_S_INITING_DRIVER`, and `PDSC_S_STOPPING_DRIVER`. `enum pds_core_dbell_bits` and `pds_core_dbell_ring` define how queue id, ring id, and descriptor index are encoded into 64-bit doorbell writes. Prototypes expose devlink, debugfs, device command, interrupt, queue, setup, notification, auxiliary bus, AdminQ, firmware, and reset functions across compilation units.

## Control Flow
The header itself has no runtime control flow, but it establishes the cross-file call graph. `main.c` owns PCI/module lifecycle and uses setup/start/stop, devlink, debugfs, auxbus, and reset prototypes. `core.c` implements setup, queues, interrupts, health, and notification. `dev.c` implements devcmd and identity. `adminq.c` implements AdminQ transport. `auxbus.c`, `devlink.c`, `debugfs.c`, and `fw.c` use the shared `pdsc` state and helper declarations.

## State And Persistence
`struct pdsc` is the persistent in-kernel state for each PCI function. It stores PCI/device pointers, debugfs dentries, BAR mappings, PF/VF relationship data, firmware state, timer/workqueue objects, devlink health reporter, firmware recovery count, identity data, interrupt metadata, locks, MMIO register pointers, AdminQ/NotifyQ queues, and reset work. All state is runtime-only.

## Dependencies And Integration Points
The header includes debugfs and devlink headers plus Pensando/AMD common, core interface, AdminQ, and interrupt ABI headers from `include/linux/pds/`. It is the internal integration point between Linux subsystems and the device firmware ABI. Exported symbols declared here are used by auxiliary client modules as well as internal objects.

## Risks
Because this header defines shared structure layout, changes can affect all implementation files and exported client assumptions. Locking fields (`devcmd_lock`, `config_lock`, `adminq_lock`, `adminq_refcnt`) encode concurrency expectations that are not type-enforced. Doorbell bit macros must match firmware/hardware ABI exactly. The `pdsc` structure mixes PF-only and VF-only fields, so lifecycle code must guard fields by `pdev->is_virtfn`.

## Test Signals
Build coverage is the primary signal for declaration consistency. Runtime signals include successful PF/VF probe, devlink operations, auxiliary-client binding, AdminQ command completion, firmware recovery, debugfs node creation, and sparse/lockdep checks around MMIO and locking annotations.
