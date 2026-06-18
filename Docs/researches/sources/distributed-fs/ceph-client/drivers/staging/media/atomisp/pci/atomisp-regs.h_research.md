# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp-regs.h

## Purpose
This header collects AtomISP PCI/MMIO register offsets, bit masks, frequency constants, CSI receiver configuration values, power-management fields, and ISP2401 CSI2+ delay-register addresses used by the AtomISP PCI core.

## Important APIs, Types, And Data
- Common PCI/MSI interrupt registers include command/status, MSI capability/address/data, interrupt control, and `PCI_I_CONTROL`.
- Merrifield-specific CSI, power, deadline, trim, RCOMP, and PM registers are defined with offsets and bit fields such as `MRFLD_PCI_CSI_CONTROL_PARPATHEN` and `MRFLD_PCI_CSI_CONTROL_CSI_READY`.
- Read/write combining flags and reset masks configure internal bus behavior through `MRFLD_PCI_I_CONTROL_*`.
- CSI lane trim and receiver-selection constants configure SH versus Arasan CSI backend selection and per-port lane settings.
- Interrupt MMIO registers include clear, status, and enable offsets.
- ISP power/frequency constants define ISPSSPM fields, requested/guaranteed frequency masks, supported ISP frequencies, HPLL frequencies, and fuse register masks.
- CSI2+ delay constants enumerate port A/B/C bases, lane offsets, TERMEN/SETTLE offsets, and absolute addresses for clock/data lane delay registers.
- `DMA_BURST_SIZE_REG` and `ISP_DFS_TRY_TIMES` provide additional PCI-core tuning constants.

## Control Flow
The header is declarative; control flow lives in PCI core code that reads/writes these offsets during probe, power transitions, CSI receiver setup, interrupt handling, dynamic frequency scaling, lane timing adjustment, and DMA tuning. Bit masks are combined with register reads/writes to enable CSI paths, select receiver backends, configure lane counts, and manage ISP power/frequency.

## State And Persistence
State is held in PCI config space and AtomISP MMIO registers programmed with these constants. Register values persist until hardware reset, power transition, or later driver writes. The header itself owns no state.

## Dependencies And Integration Points
It depends on `BIT()` being available from includers and is consumed by AtomISP PCI/platform code. It integrates hardware register programming with sensor CSI topology from `atomisp_platform.h`, MMU/HMM memory behavior, interrupt handling, and power/frequency management.

## Risks
- Register offsets and masks are hardware-specific; using the wrong constants for a SoC revision can break CSI, interrupts, or power management.
- Absolute CSI2+ delay addresses assume a particular MMIO layout and should be gated by hardware generation.
- Some constants represent PCI config-space offsets while others are MMIO offsets; call sites must use the correct accessors.
- Frequency constants are integer MHz-like encodings; mismatched HPLL/fuse interpretation can select unsupported clocks.

## Test Signals
Validation should include PCI probe register-access smoke tests, interrupt enable/status/clear behavior, CSI receiver selection for each supported port/lane configuration, Merrifield/Cherry Trail generation gating, ISP power on/off state transitions, dynamic frequency requests with timeout handling using `ISP_DFS_TRY_TIMES`, and readback verification for CSI2+ settle/termen tuning registers.
