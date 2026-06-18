# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci1.c

Purpose: Implements the GRPCI1 LEON PCI host bridge driver, including config-space access, target BAR setup, shared interrupt demuxing, and PCI error handling.

Important APIs/types/functions: `struct grpci1_regs` maps APB bridge registers; `struct grpci1_priv` embeds `leon_pci_info`, register pointer, resources, IRQ maps, error mask, and AHB/PCI windows. Config helpers `grpci1_cfg_r{8,16,32}()` and `grpci1_cfg_w{8,16,32}()` select the bus in `cfg_stat`, access config space via LEON bypass loads/stores, swab values for little-endian PCI, and handle master aborts. `grpci1_map_irq()`, `grpci1_irq`, `grpci1_pci_flow_irq()`, `grpci1_err_interrupt()`, `grpci1_hw_init()`, and `grpci1_of_probe()` are the main driver pieces.

Control flow: Probe allows only one host, maps APB registers, verifies host-slot mode, BAR1 size, and byte twisting, maps PCI I/O/config windows, requests resource ranges, initializes hardware target mappings, creates virtual IRQs for INTA-D and errors, installs a LEON IRQ demux, enables selected error interrupts, and calls `leon_pci_init()` to enumerate the bus.

State and persistence: Persistent runtime state is the single global `grpci1priv`, bridge MMIO state, target BAR programming, resource claims, virtual IRQs, and PCI devices. Error policy is controlled by the optional `all_pci_errors` OF property.

Dependencies and integration points: It depends on LEON bypass MMIO, OF platform probing, `irq_of_parse_and_map()`, LEON IRQ helpers, generic PCI ops, and common LEON PCI initialization.

Risks and test signals: Single-instance global state prevents multiple GRPCI1 cores. Config abort clearing writes bridge PCI status and must not mask real errors. Tests include host-slot rejection, byte-twisting requirement, config reads of absent devices, INTx demux, PCI error injection, resource conflicts, and enumeration up to bus 15/device 15.
