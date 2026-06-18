<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c

## Purpose
`aer_inject.c` provides a misc-device based AER software injector for testing AER handling without hardware faults. Userspace writes a packed `struct aer_error_inj` to `/dev/aer_inject`, and the module simulates device and root-port AER config registers before injecting the AER service IRQ.

## Important APIs, Types, and Functions
Important local types are `struct aer_error_inj`, `struct aer_error`, and `struct pci_bus_ops`. Core functions include `aer_inject_write()`, `aer_inject()`, `pci_bus_set_aer_ops()`, `aer_inj_read_config()`, `aer_inj_write_config()`, `find_pci_config_dword()`, and cleanup in `aer_inject_exit()`. The module uses `pcie_port_find_device()` to locate the AER service device and `irq_inject_interrupt()` to trigger its IRQ.

## Control Flow and State
Injection validates `CAP_SYS_ADMIN`, copies userspace payload, finds the target device plus root port or RCEC, checks AER capability positions and current masks, allocates or updates simulated `aer_error` records under `inject_lock`, populates device status/header log fields, synthesizes root status/source ID, overrides bus `pci_ops` for target/root buses, then injects the service IRQ. Reads and writes to relevant AER config dwords are intercepted; write-one-to-clear status semantics are emulated by XOR for RW1C fields. Module exit restores original bus ops and frees injected state.

## Dependencies and Integration Points
The injector depends on `CONFIG_PCIEAER`, generic IRQ injection, miscdevice infrastructure, and a registered AER port service on the root port/RCEC. It integrates with `aer.c` by making its regular IRQ and config-space read paths see the synthetic records.

## Risks and Test Signals
Risks include global bus-ops substitution races, stale injected records if an injection fails after partial setup, limited dword-only config emulation, and the `aer_mask_override` mask updates using logical negation instead of bitwise complement semantics. Test signals include injecting masked/unmasked correctable and uncorrectable errors, multiple errors on one root, RCEC targets, module unload after failures, and verifying original `pci_ops` restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/aer_inject.c -->
