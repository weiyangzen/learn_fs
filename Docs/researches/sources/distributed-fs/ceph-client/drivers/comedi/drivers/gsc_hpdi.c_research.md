## sources/distributed-fs/ceph-client/drivers/comedi/drivers/gsc_hpdi.c

### Purpose
`gsc_hpdi.c` is the Comedi PCI driver for General Standards PCI/PMC HPDI32 high-speed parallel digital interface boards. It implements receive-mode, command-driven 32-bit digital input using PLX9080 chained DMA; transmit is documented as unsupported.

### Important APIs, Types, And Functions
`struct hpdi_private` owns PLX MMIO, DMA buffers, descriptor ring metadata, FIFO sizes, DMA descriptor index, finite sample count, and block size. Main functions are `gsc_hpdi_init_plx9080()`, `gsc_hpdi_init()`, `gsc_hpdi_setup_dma_descriptors()`, `gsc_hpdi_cmd_test()`, `gsc_hpdi_cmd()`, `gsc_hpdi_interrupt()`, `gsc_hpdi_drain_dma()`, `gsc_hpdi_cancel()`, `gsc_hpdi_auto_attach()`, and `gsc_hpdi_detach()`.

### Control Flow
Attach enables PCI bus mastering, maps PLX BAR0 and HPDI BAR2, initializes PLX DMA mode, requests IRQ, allocates four coherent 64 KiB data buffers and 256 coherent descriptors, sets the default descriptor block size, creates one DIO command subdevice, and resets/enables board interrupts. Command setup rejects output mode, resets RX FIFO and DMA, writes the first descriptor pointer to PLX, starts DMA0, initializes finite or indefinite `dio_count`, clears RX error flags, enables RX-full interrupt, and enables RX. Interrupts verify PLX interrupt ownership, clear HPDI/PLX interrupt sources, drain all completed DMA blocks into the Comedi buffer, detect RX overrun/underrun, and signal EOA when finite count reaches zero.

### State, Persistence, And Dependencies
Persistent state includes coherent DMA buffers/descriptors, circular descriptor topology, subdevice direction bits, block size from `INSN_CONFIG_BLOCK_SIZE`, FIFO size readings, IRQ ownership, and PLX/board MMIO mappings. Dependencies include `plx9080.h`, coherent DMA APIs, Comedi async buffers, shared IRQ handling, and spinlock-protected PLX DMA control registers.

### Integration Points
The driver binds PLX9080 subsystem ID `0x2400`, uses `comedi_pci_auto_config()`, and exposes block-size configuration plus `SDF_CMD_READ` on a 32-channel DIO subdevice.

### Risks
Only RX path is implemented. Descriptor/block-size changes affect interrupt cadence and buffer accounting. The drain loop infers completed blocks from PLX current address and has only an XXX note for overrun detection. Finite counts are counted in 32-bit samples while DMA block sizing is byte-based. DMA descriptor alignment and cleanup on partial attach failure are critical.

### Test Signals
Test DMA allocation failure unwind, descriptor lengths including non-word-aligned requests, finite and continuous commands, chanlist ordering validation, RX FIFO overrun/underrun flags, shared IRQ filtering, cancellation, repeated block-size reconfiguration, and detach with active DMA.
