## sources/distributed-fs/ceph-client/drivers/comedi/drivers/icp_multi.c

### Purpose
`icp_multi.c` drives the Inova ICP_MULTI PCI board for synchronous AI, AO, DI, and DO. Comments state interrupts, counters, and DMA are not implemented.

### Important APIs, Types, And Functions
The file defines ADC/DAC/DIO/interrupt register bits, shared analog range tables, `range_codes_analog[]`, and callbacks `icp_multi_ai_insn_read()`, `icp_multi_ao_insn_write()`, `icp_multi_di_insn_bits()`, `icp_multi_do_insn_bits()`, `icp_multi_reset()`, and `icp_multi_auto_attach()`.

### Control Flow
Attach enables PCI, maps BAR2, allocates four subdevices, resets board outputs/interrupt status, and configures AI/AO/DI/DO. AI builds an ADC CSR from channel, range, and single-ended/differential mode, starts each conversion, delays briefly, polls busy clear, and reads 12-bit data from the AI register. AO selects channel/range, waits until DAC not busy, writes the sample, starts conversion, and stores readback. DIO uses direct 16-bit/8-bit register reads and writes.

### State, Persistence, And Dependencies
State is the mapped MMIO region, AO readback, DO state, and board output state after reset. The driver depends on Comedi PCI helpers, Comedi timeout polling, port-width MMIO accessors, and range/reference encoding in Comedi chanspecs.

### Integration Points
PCI ID `PCI_VENDOR_ID_ICP, 0x8000` auto-configures this driver. Comedi users see four simple instruction-only subdevices.

### Risks
Counter and interrupt registers are reset but not exposed. AI does not validate differential channel range beyond composing the CSR. Reset forces all AO channels to 0 V in 0..5 V range, which may be observable on attach. AO readback depends on successful readback allocation only.

### Test Signals
Test PCI probe and BAR2 mapping, reset side effects, all AI ranges and references, AI timeout, AO busy timeout and readback, DI/DO widths, interrupt status clearing, and detach through `comedi_pci_detach()`.
