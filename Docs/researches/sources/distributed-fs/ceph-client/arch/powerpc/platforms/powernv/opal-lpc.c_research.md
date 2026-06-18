## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-lpc.c

### Purpose
`opal-lpc.c` provides LPC bus access on PowerNV through OPAL. It installs special ISA/PCI I/O callbacks for non-memory-mapped LPC buses and optionally exposes raw LPC IO/MEM/FW address spaces through debugfs.

### Important APIs, Types, And Functions
Important functions are byte/word/long accessors `opal_lpc_in*()` and `opal_lpc_out*()`, string I/O helpers, `lpc_debug_read()`, `lpc_debug_write()`, `opal_lpc_init_debugfs()`, and `opal_lpc_init()`. `struct lpc_debugfs_entry` records the OPAL LPC address type.

### Control Flow
Boot scans for an available primary `ibm,power8-lpc` node, records its chip ID, and either initializes a non-PCI ISA bridge for memory-mapped LPC ranges or installs `ppc_pci_io` callbacks backed by `opal_lpc_read()` and `opal_lpc_write()`. Debugfs creates `lpc/io`, `lpc/mem`, and `lpc/fw`. Debugfs reads and writes choose 1-, 2-, or 4-byte accesses based on alignment and address type, then adjust endian/layout quirks around OPAL's right-justified big-endian 32-bit data word.

### State, Persistence, And Dependencies
The main state is the selected `opal_lpc_chip_id` and debugfs entries. Real persistence is in LPC devices and firmware. Dependencies include OPAL LPC calls, OF primary bus properties, ISA bridge setup, `ppc_pci_io`, endian conversion, and user-copy APIs.

### Integration Points
Low-level I/O operations used by ISA-style drivers can route through this file when the LPC bus is not directly mapped. Debugfs is a privileged diagnostic and firmware access surface.

### Risks
Endian handling for unaligned and small accesses is delicate, especially on little-endian kernels. The driver supports only one primary LPC bus despite the OPAL API allowing more. Debugfs exposes raw firmware/LPC address spaces and uses manually allocated entries without removal cleanup.

### Test Signals
Tests should cover mapped and non-mapped LPC DT setups, invalid chip ID/port bounds, unaligned word/long accesses, little-endian debugfs byte layout, partial user-copy failures, debugfs IO/MEM/FW reads/writes, and ISA driver access through `ppc_pci_io`.
