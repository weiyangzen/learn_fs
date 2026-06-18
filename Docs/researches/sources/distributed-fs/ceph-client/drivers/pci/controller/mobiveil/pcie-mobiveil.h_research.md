## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.h

Purpose: Shared Mobiveil PCIe register definitions, private data structures, operation hooks, and helper prototypes for the common and host implementations.

Important APIs, types, and functions: The header defines PAB register offsets, page-selection macros, LTSSM constants, PIO control/status, interrupt bits, APIO/PPIO address-map register constructors, MSI register offsets, window type constants, limits, and retry constants. `struct mobiveil_msi` tracks MSI domain and bitmap. `struct mobiveil_root_port` stores config aperture, outbound config resource, root-port ops, IRQ/domain state, MSI state, and host bridge. `struct mobiveil_pcie` stores platform device, CSR/APB bases, physical base, window counts/counters, PAB ops, and root-port data. Inline wrappers expose typed CSR reads/writes.

Control flow: no executable flow beyond inline wrappers delegating to `mobiveil_csr_read()`/`mobiveil_csr_write()`. Other Mobiveil files use the definitions to program windows, interrupts, MSI, and link state.

State and persistence: the defined structures hold volatile runtime state allocated by platform drivers. No persistent state exists.

Dependencies and integration points: Linux PCI, IRQ, MSI APIs, the local `../../pci.h`, and all Mobiveil implementation files. It is the ABI between platform-specific drivers and common host/core code.

Risks: Register macros encode hardware layout and window stride; mistakes propagate broadly. MSI vector count is fixed at 16. `ops` and `rp.ops` are optional in some paths but dereferenced in selected helpers, so platform initialization must match expectations. Inline accessors use literal sizes `0x4`, `0x2`, and `0x1`.

Test signals: compile all Mobiveil drivers, static checks for macro expansion, runtime window programming across all indices, MSI allocation up to `PCI_NUM_MSI`, and platform override ops behavior.
