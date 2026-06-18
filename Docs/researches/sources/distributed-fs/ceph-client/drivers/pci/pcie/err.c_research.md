<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c

## Purpose
`err.c` implements generic PCIe error recovery shared by AER, DPC, EDR, and firmware-reported AER. It walks the affected bridge subtree, calls driver `pci_error_handlers` in the required order, coordinates resets, updates PCI channel state, and emits uevents.

## Important APIs, Types, and Functions
The central exported function is `pcie_do_recovery(struct pci_dev *dev, pci_channel_state_t state, pci_ers_result_t (*reset_subordinates)(struct pci_dev *pdev))`. Key helpers include `merge_result()`, `report_error_detected()`, `report_mmio_enabled()`, `report_slot_reset()`, `report_resume()`, `report_perm_failure_detected()`, `pci_pm_runtime_get_sync()`, `pci_pm_runtime_put()`, and `pci_walk_bridge()`.

## Control Flow and State
Recovery chooses the affected bridge: Root Port, Downstream Port, RCEC, and RCiEP recover from themselves; endpoints recover via their upstream bridge. It runtime-resumes all affected devices, broadcasts `error_detected()` with frozen or normal channel state, optionally broadcasts `mmio_enabled()`, invokes the supplied subordinate reset function when a reset is needed or state is frozen, broadcasts `slot_reset()` if requested, and finally broadcasts `resume()`. On success, native AER ownership allows clearing device and nonfatal AER status. On failure, it calls `error_detected(...perm_failure)` and leaves devices disconnected.

## Dependencies and Integration Points
The file depends on PCI driver error-handler callbacks, runtime PM, AER status helpers, `pci_dev_set_io_state()` from `pci.h`, RCEC/RCiEP handling, and reset callbacks provided by AER or DPC (`aer_root_reset()` or `dpc_reset_link()`). The PCIe port driver itself provides error handlers so port-service children can be reset.

## Risks and Test Signals
Risks include incorrect result merging, devices without callbacks aborting recovery for an entire subtree, runtime PM imbalance, state transitions blocked by permanent failure, and bridge selection mistakes for RCEC/RCiEP. Tests should inject AER/DPC failures across endpoints and bridges, cover callback result combinations, missing driver handlers, reset failures, runtime-suspended devices, and successful clearing under native AER only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/err.c -->
