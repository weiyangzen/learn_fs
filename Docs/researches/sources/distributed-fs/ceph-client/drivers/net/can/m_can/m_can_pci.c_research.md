# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_pci.c

## Purpose
`m_can_pci.c` is the PCI glue for Intel PCI-attached Bosch M_CAN controllers. It maps PCI BAR MMIO into the common M_CAN transport interface and registers an `m_can_classdev`.

## Important APIs, Types, And Functions
- `struct m_can_pci_priv` embeds `struct m_can_classdev` and stores the mapped BAR base.
- `iomap_read_reg()`, `iomap_write_reg()`, `iomap_read_fifo()`, and `iomap_write_fifo()` implement `m_can_ops` with `readl()`/`writel()` and 32-bit FIFO loops.
- `m_can_pci_probe()` performs managed PCI enable/iomap, allocates the class device, allocates one IRQ vector, fills M_CAN class fields, registers the class device, enables wrapper interrupt control, and enables runtime PM autosuspend.
- `m_can_pci_remove()` disables runtime PM and wrapper interrupt control, unregisters and frees the class device, and frees IRQ vectors.
- PM callbacks forward to `m_can_class_suspend()` and `m_can_class_resume()`.

## Control Flow
Probe enables the PCI device, sets bus master, maps BAR0, allocates the common netdev/class private area, configures the class for runtime PM clock support and edge-triggered IRQ behavior, then calls the common registration path. After successful registration, it writes `CTL_CSR_INT_CTL_OFFSET` to enable the CAN wrapper interrupt output.

## State And Persistence
State is limited to the mapped MMIO base and the embedded common class state. Runtime PM state is managed through the PCI device. No persistent storage is used.

## Dependencies And Integration Points
The file depends on PCI core, runtime PM, netdevice, and the exported M_CAN class APIs. It supports Intel PCI IDs `0x4bc1` and `0x4bc2` with a 200 MHz CAN clock from `driver_data`.

## Risks And Edge Cases
- The driver marks interrupts as edge-triggered, so correctness depends on common IR drain behavior.
- FIFO access increments `void *` pointers as a GNU C extension and assumes aligned 32-bit transfers.
- Wrapper interrupt enable happens after class registration; failures after that point must disable it during remove.

## Test Signals
Validate probe/remove on supported Intel devices, MSI and legacy IRQ behavior, runtime PM autosuspend/resume, interrupt delivery after IR drain, and TX/RX over MMIO FIFO.
