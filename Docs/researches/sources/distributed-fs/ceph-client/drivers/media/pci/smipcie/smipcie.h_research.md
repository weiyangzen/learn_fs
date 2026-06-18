<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie.h

Purpose: shared header for the SMI PCIe driver. It defines register offsets, bit masks, board/frontend/DMA configuration constants, main device/port/IR structs, MMIO helper macros, and IR function prototypes.

Important APIs, types, and functions: key types are `smi_cfg_info`, `smi_rc`, `smi_port`, and `smi_dev`. Important constants include MSI interrupt bits, I2C software-control bits, DTV/DMA register addresses, `SMI_TS_DMA_BUF_SIZE`, board type IDs, TS DMA mode IDs, and frontend type IDs. Macros `smi_read()`, `smi_write()`, `smi_andor()`, `smi_set()`, and `smi_clear()` wrap MMIO access.

Control flow: not executable, but all main/IR code uses these definitions to program hardware and share device state.

State and persistence: defines runtime memory layout only. `smi_port` owns DMA register selections and DVB/frontend state; `smi_dev` owns PCI/MMIO, ports, I2C buses, and IR.

Dependencies and integration points: Linux PCI, DMA, I2C algo-bit, workqueues, RC core, DVB core/demux/net.

Risks: MMIO macros assume a local variable named `dev`, which can hide errors. Register constants are broad and hardware-specific with little type safety. `DMA_PORTC_CONTROL_REG_BASE` and `DMA_PORTD_CONTROL_REG_BASE` share the same value, which is harmless if unused but risky if future code enables those ports.

Test signals: full driver build, sparse checks for macro misuse, successful port A/B register programming, I2C bit toggling, and correct IRQ bit mapping for both DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/smipcie.h -->
