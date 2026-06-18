<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci.h -->
# sources/distributed-fs/ceph-client/drivers/pci/pci.h

## Purpose
`pci.h` is the private PCI core header used by the PCI and PCIe service implementations. It centralizes internal constants, prototypes, small helpers, capability-search macros, PCIe link-speed conversions, reset/power-management contracts, resource helpers, SR-IOV metadata, AER/DPC/PTM/ASPM hooks, ACPI/OF integration stubs, and config mechanism definitions. It is not a standalone implementation; it is the connective contract between PCI core files such as enumeration, resource assignment, power management, error recovery, and the PCIe port-service drivers under `drivers/pci/pcie/`.

## Important APIs, Types, and Functions
Key macros include `PCI_FIND_NEXT_CAP()` and `PCI_FIND_NEXT_EXT_CAP()`, both TTL-limited config-space capability walkers parameterized by a config read function prefix. Link helpers include `PCIE_LNKCAP_SLS2SPEED()`, `PCIE_LNKCAP2_SLS2SPEED()`, `PCIE_LNKCTL2_TLS2SPEED()`, `PCIE_SPEED2MBS_ENC()`, `pcie_dev_speed_mbps()`, `pcie_update_link_speed()`, and `enum pcie_link_change_reason`.

Important types include `struct pci_cap_saved_state`, `struct pci_sriov`, `struct aer_err_info`, `struct rcec_ea`, `struct pci_eq_presets`, `struct pci_dev_reset_methods`, and `struct pci_reset_fn_method`. Exported internal contracts include AER (`pci_aer_init()`, `pci_aer_clear_status()`, `aer_get_device_error_info()`), DPC (`dpc_process_error()`, `dpc_reset_link()`), RCEC walking/linking, ASPM/LTR save-restore and policy hooks, PTM save/restore hooks, and `pcie_do_recovery()`.

## Control Flow and State
Most routines declared here are invoked by PCI device setup, suspend/resume, hotplug, and error paths. The saved-capability structures support suspend/resume persistence for AER, DPC, PTM, LTR, L1SS, SR-IOV, and PCIe base capability state. `pci_dev_set_io_state()` is a small atomic state machine for PCI error recovery: permanent failure is sticky, frozen can only transition from normal, and normal can only transition from frozen unless permanent failure is already set. `priv_flags` bits record lifecycle and link/error state such as added/removed, DPC recovered/recovering, link changed/changing, LBMS seen, and driver binding allowance.

## Dependencies and Integration Points
This header depends on core kernel PCI definitions, bitfield helpers, tracepoints, and config options. It is heavily conditional: unavailable features compile to no-op or error-returning inline stubs, allowing callers to remain simple across many kernel configurations. It integrates with `pcie/aer.c`, `dpc.c`, `aspm.c`, `bwctrl.c`, `err.c`, `pme.c`, `portdrv.c`, `ptm.c`, ACPI/OF glue, controller drivers, quirks, hotplug, and endpoint drivers that call public PCI APIs backed by these internal implementations.

## Risks and Test Signals
Risks are mostly contract drift: adding fields to saved state without adjusting buffer sizes, changing capability search semantics, weakening ordering around `priv_flags`, or using PCIe helpers on non-PCIe devices. Tests should exercise suspend/resume of AER/DPC/PTM/ASPM-capable devices, error recovery state transitions, config-space capability walking with malformed lists, link speed reporting and retraining, hotplug with DPC, and builds across feature combinations where stubs replace implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci.h -->
