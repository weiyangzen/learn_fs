## sources/distributed-fs/ceph-client/arch/mips/pci/pci.c

### Purpose
This small file provides common MIPS PCI globals and helpers shared by PCI implementations: default minimum I/O and memory values, cache-line-size initialization, and user-visible resource address fixup.

### Important APIs, Types, And Functions
`PCIBIOS_MIN_IO` and `PCIBIOS_MIN_MEM` are exported globals. `pcibios_set_cache_line_size()` computes the highest available data/secondary/tertiary cache line size and stores `pci_dfl_cache_line_size` in dwords. `pci_resource_to_user()` translates resource starts through `fixup_bigphys_addr()`.

### Control Flow
At `arch_initcall()`, cache line size is derived from CPU cache helpers and must be nonzero. Resource translation is called by PCI sysfs/proc paths when presenting BAR ranges to userspace.

### State, Persistence, And Dependencies
Persistent state is `pci_dfl_cache_line_size` and exported minimum-resource globals. Dependencies include MIPS CPU cache helpers and big physical address fixups.

### Integration Points
Platform files set `PCIBIOS_MIN_IO/MEM`; generic PCI device enable and user-resource reporting consume these values.

### Risks
`BUG_ON(!lsize)` makes broken CPU cache reporting fatal. `pci_resource_to_user()` sets `end` from the un-fixed resource start, which should be checked for consistency when big physical address fixups change `start`.

### Test Signals
Boot logs under PCI debug, `lspci -vv` cache line values, and sysfs resource files on high physical address systems validate this file.
