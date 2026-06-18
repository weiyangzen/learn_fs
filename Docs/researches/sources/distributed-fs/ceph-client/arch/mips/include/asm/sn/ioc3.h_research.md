<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h

Purpose: Defines the SGI IOC3 PCI multifunction chip register layout and bit definitions for serial, SuperIO, keyboard/mouse, parallel port, GPIO, Ethernet DMA, SSRAM, PCI status, and subsystem IDs.

Important APIs/types/functions: Register structs `ioc3_serialregs`, `ioc3_uartregs`, `ioc3_sioregs`, `ioc3_ethregs`, `ioc3_serioregs`, `ioc3`; DMA descriptors `ioc3_erxbuf`, `ioc3_etxd`; base offsets `IOC3_SIO_*`, bytebus offsets, PCI status flags, KM/serial status/control masks, SIO interrupt masks, GPIO masks, Ethernet control/status/ring masks, MII access masks, and IOC3 subsystem IDs.

Control flow: Drivers map IOC3 PCI BAR space to `struct ioc3`, then configure subblocks: reset/control SIO, program serial rings, service SIO interrupts, configure GPIO/PHY reset, manage Ethernet RX/TX rings, and access SuperIO UART/RTC/parallel registers at byte offsets.

State and persistence: Hardware state includes PCI config/status, GPIO latches, keyboard/mouse FIFOs, serial DMA rings and producer/consumer pointers, Ethernet rings, MAC/MII registers, interrupt enables, and SSRAM diagnostic space. The header itself owns no software state.

Dependencies and integration points: Depends only on Linux integer types. Integrated by SGI IOC3 serial, Ethernet, keyboard/mouse, MFD, and PCI bridge drivers.

Risks: The C structs must match hardware offsets exactly; padding or type-size changes are dangerous. The file contains legacy duplicate fields/macros (`ioc3_etxd.cmd`, `INT_OUT_MODE_*`) that consumers tolerate but should not be expanded. DMA ring alignment constants are hardware requirements.

Test signals: IOC3 driver compile, serial console, keyboard/mouse, Ethernet RX/TX under load, MII access, interrupt masking, and PCI subsystem detection tests are relevant.

Source read size: 606 lines, 21824 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h -->
