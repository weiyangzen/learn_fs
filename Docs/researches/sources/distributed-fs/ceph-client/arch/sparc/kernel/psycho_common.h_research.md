# sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.h

Purpose: declares shared PSYCHO-family PCI controller helpers and defines config-space address encoding used by common error and setup code.

Important APIs/types/functions: macros `PSYCHO_CONFIG_BASE()` and `PSYCHO_CONFIG_ENCODE()` build controller config-space addresses. `psycho_pci_config_mkaddr()` returns a config-space pointer for bus/devfn/register. `enum psycho_error_type` names UE, CE, and PCI error contexts. Function declarations cover IOMMU checking, PCI error IRQ handling, IOMMU init, and PBM common init.

Control flow: the only executable logic is the inline config address constructor, which ORs controller config-space base with encoded bus, device/function, and register fields.

State and persistence: no state is owned by this header.

Dependencies and integration points: consumed by PSYCHO-derived PCI controller implementations and `psycho_common.c`. It depends on `pci_pbm_info`, platform devices, IRQ return types, and the U2P configuration-space address format.

Risks: config address bit packing is hardware-defined; a small macro error would break all config reads/writes for PSYCHO-family controllers.

Test signals: PCI config space enumeration on PSYCHO-derived controllers, successful reads of root bus PCI status in error handlers, and compile coverage of all declared common functions.
