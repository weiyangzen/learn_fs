## sources/distributed-fs/ceph-client/drivers/dma/dw/idma32.c

Purpose: Register-variant implementation for Intel iDMA32 controllers, including optional crossbar programming for newer PSE DMA devices.

Important APIs/types/functions: exports `idma32_dma_probe()` and `idma32_dma_remove()`. Provides channel init callbacks `idma32_initialize_chan_generic()` and `idma32_initialize_chan_xbar()`, suspend/resume with drain support, byte/block conversion, CTL_LO preparation, FIFO partitioning, and enable/disable wrappers.

Control flow: probe allocates `struct dw_dma`, selects xbar or generic channel initialization based on platform-data quirks, installs iDMA32-specific callbacks, and delegates to `do_dma_probe()`. Xbar initialization programs channel ID access, transfer mode, snoop bits, PCI devfn selection, RX/TX selection, request-line extensions, and channel CFG registers. Enable/disable partition FIFOs before/after core enable state changes.

State and persistence: modifies iDMA32-specific MMIO registers for channel control, source/destination fill-in, xbar selection, register access channel ID, and FIFO partition. Runtime state remains in shared `struct dw_dma`.

Dependencies and integration: used by internal platform data for Merrifield and Elkhart Lake/PSE PCI/ACPI IDs. Depends on PCI device identity for xbar slave devfn selection.

Risks and test signals: xbar mode depends on correct slave PCI device association and direction mapping; FIFO partition programming affects all channels. Test Intel iDMA32 devices with MEM_TO_DEV and DEV_TO_MEM clients, xbar and non-xbar paths, drain terminate, maxburst encoding, and repeated enable/disable cycles.
