# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_main.c

## Purpose
`idpf_main.c` is the PCI module entry point for the IDPF Linux driver. It binds Intel PF/VF PCI IDs or a generic Ethernet programming-interface class ID, determines PF versus VF behavior, allocates the adapter, maps core BAR regions, creates driver workqueues, initializes device-specific operation tables, starts the asynchronous hard-reset/driver-load path, and tears everything down on remove or shutdown.

## Important APIs, types, and functions
- Module/PCI declarations: `MODULE_DESCRIPTION`, namespace imports, `idpf_pci_tbl`, `idpf_driver`, and `module_pci_driver(idpf_driver)`.
- Device type selection: `idpf_get_device_type()` and `idpf_dev_init()`.
- PCI lifecycle: `idpf_probe()`, `idpf_remove()`, and `idpf_shutdown()`.
- Hardware BAR setup: `idpf_cfg_hw()`.
- External lifecycle hooks used here: `idpf_vc_core_deinit()`, `idpf_deinit_dflt_mbx()`, `idpf_sriov_configure()`, `idpf_init_task`, `idpf_service_task`, `idpf_mbx_task`, `idpf_statistics_task`, and `idpf_vc_event_task`.

## Control flow
On probe, the driver allocates `struct idpf_adapter`, defaults requested TX/RX queue model to split queue, enables the PCI device, requests BAR0, enables PCIe PTM if available, configures a 64-bit coherent DMA mask, sets bus master, and stores adapter in PCI driver data. It then allocates init, service, mailbox, stats, and virtchnl-event workqueues, initializes debug message level, selects PF or VF device ops, maps the mailbox and reset-status windows using device-specific static register info, initializes adapter mutexes and delayed work items, initializes reset register descriptors, sets `IDPF_HR_DRV_LOAD`, and queues `vc_event_task` to perform the real driver-load reset and virtchnl initialization.

Device-type selection uses explicit PCI device IDs when available. For the generic class entry, `idpf_get_device_type()` temporarily maps the VF mailbox ARQBAL offset, writes a test value, and treats a successful read-back as VF; otherwise it selects PF. VF initialization sets `adapter->crc_enable`, while PF initialization uses PF device ops.

Remove sets `IDPF_REMOVE_IN_PROG`, cancels virtchnl event work, disables SR-IOV VFs if active, deinitializes virtchnl core, triggers a function reset to leave hardware clean, deinitializes the default mailbox, unregisters and frees any stale netdevs, destroys all workqueues, frees each vport config and coalescing array, frees adapter arrays and connection manager, destroys mutexes, clears PCI driver data, and frees the adapter. Shutdown cancels service/event work, deinitializes virtchnl and mailbox, and puts the device into D3hot on poweroff.

## State and persistence behavior
This file owns top-level adapter allocation and destruction, PCI driver data, workqueue lifetime, BAR mapping metadata in `adapter->hw`, adapter mutex lifetime, and the initial reset/load flags. It does not itself register netdevs or allocate vports; it starts the reset/event path that delegates that work to `idpf_lib.c`. BAR mappings are device-managed (`devm_ioremap`) for mailbox and reset windows.

## Dependencies and integration points
The file depends on Linux PCI, DMA, workqueue, module, and power-management APIs. It includes device ID definitions, VF register definitions for class-based detection, virtchnl declarations, and IDPF core headers. It integrates with PF/VF device ops initializers, register ops, virtchnl core init/deinit, mailbox setup, SR-IOV, and all delayed tasks implemented in `idpf_lib.c`.

## Risks and edge cases
- Generic class PF/VF detection writes to a VF mailbox offset; correctness depends on PF hardware not echoing the test value and the mapping being safe before normal BAR setup.
- Probe performs most initialization asynchronously. Any failure after queueing `vc_event_task` must be handled by later deinit paths, not normal probe unwinding.
- Remove must handle partially initialized adapters and reset-recovery failures, including stale registered netdevs and active VFs.
- Workqueue destroy ordering must follow cancellation/deinit paths so no delayed work can run after adapter memory is freed.
- `idpf_cfg_hw()` relies on `dev_ops.static_reg_info[0]` and `[1]` being initialized correctly for PF/VF before mapping.

## Test signals
Build and module load/unload for PF and VF IDs, probe through generic class ID, DMA mask failure injection, BAR request/map failure injection, PCIe PTM supported/unsupported paths, asynchronous init failure cleanup, remove during hard reset recovery, shutdown/poweroff behavior, SR-IOV active remove, and workqueue lifetime checks with KASAN/lockdep are the main validation signals.
