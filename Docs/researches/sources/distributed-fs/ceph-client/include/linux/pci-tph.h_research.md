# Research: sources/distributed-fs/ceph-client/include/linux/pci-tph.h

Purpose: `pci-tph.h` declares PCIe TLP Processing Hint helpers for enabling TPH and managing steering tags, including different tags for volatile and persistent memory targets.

Important APIs/types/functions: `enum tph_mem_type` differentiates volatile memory and persistent memory. Enabled builds export `pcie_tph_set_st_entry()`, `pcie_tph_get_cpu_st()`, `pcie_disable_tph()`, `pcie_enable_tph()`, `pcie_tph_get_st_table_size()`, and `pcie_tph_get_st_table_loc()`. Disabled stubs return `-EINVAL` or no-op for the main operations.

Control flow and state: drivers enable TPH in a selected mode, query or program steering-tag table entries, use CPU/memory-type-specific tags, and disable TPH on teardown. State is in PCIe TPH capability registers and steering tag tables.

Dependencies and integration points: depends on PCI core and PCI Firmware Specification steering-tag semantics. It integrates with performance-sensitive PCIe devices, NUMA/cache locality policy, and persistent-memory targeting.

Risks and test signals: risks include wrong memory-type steering tag, table index overflow, enabling unsupported modes, and missing disabled-build handling. Tests should cover capability discovery, table size/location reads, tag programming, CPU tag lookup, PM vs VM tag selection, and device removal cleanup.
