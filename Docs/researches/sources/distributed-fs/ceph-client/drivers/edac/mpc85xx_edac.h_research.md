# sources/distributed-fs/ceph-client/drivers/edac/mpc85xx_edac.h

## Purpose
Defines the MPC85xx EDAC register offsets, bit masks, logging wrapper, and private data structures shared by the MPC85xx EDAC implementation. It is the hardware contract for the L2-cache and PCI/PCIe error paths in `mpc85xx_edac.c`.

## Important APIs, Types, And Functions
- `MPC85XX_L2_*` offsets identify L2 injection, capture, detect, disable, interrupt-enable, attribute, address, and control registers.
- `L2_EIE_*` and `L2_EDE_*` masks define interrupt-enable bits and CE/UE classification for L2 errors.
- `PCI_EDE_*` masks classify PCI error detect bits, including parity masks and multi-error status.
- `MPC85XX_PCI_*` offsets describe PCI/PCIe error detect, capture, enable, attribute, address, data, timer, and capability capture registers.
- `struct mpc85xx_l2_pdata` and `struct mpc85xx_pci_pdata` hold EDAC-private per-device state.

## Control Flow
The header has no executable control flow. Its constants are consumed during probe to map and program hardware registers, during check/ISR paths to classify errors, and during remove to restore original masks.

## State And Persistence
No state is stored in the header. The declared private structures persist inside EDAC control blocks allocated by the driver and carry mapped base addresses, IRQs, device names, indexes, and PCIe-vs-PCI mode.

## Dependencies And Integration Points
Integrated tightly with `mpc85xx_edac.c`, the EDAC core, and Freescale hardware register layouts. The bit definitions are used with big-endian MMIO accessors and OF-provided resources.

## Risks And Edge Cases
Incorrect masks directly affect whether hardware errors are reported as CE, UE, parity, or non-parity. The header groups L2 configuration, multibit, and tag parity under UE; if hardware semantics differ by SoC revision, the C driver will inherit that classification. The structures store raw `void __iomem *` bases and IRQ integers, so lifetime is controlled entirely by the probe/remove implementation.

## Test Signals
Compile coverage with and without `CONFIG_PCI`, static checks that register offsets match the hardware manual, and runtime tests that injected L2 and PCI status bits map to the expected EDAC handler calls.
