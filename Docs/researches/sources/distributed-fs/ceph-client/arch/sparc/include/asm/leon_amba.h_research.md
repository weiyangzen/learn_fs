# sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_amba.h` describes LEON AMBA Plug and Play buses, UART/timer/IRQ register maps, vendor/device IDs, and exported AMBA discovery state. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 267 lines, 8283 bytes. Primary surface: `struct amba_prom_registers`, UART/PS2/timer/IRQ bit macros, `struct leon3_irqctrl_regs_map`, `struct leon3_apbuart_regs_map`, `struct leon3_gptimer_regs_map`, AMBA device tables, `_amba_init()`, AMBA globals, vendor/device id macros, and `amba_vendor/amba_device`. Symbol scan highlights: `LEON_AMBA_H_INCLUDE`, `struct amba_prom_registers`, `LEON_REG_UART_STATUS_DR`, `LEON_REG_UART_STATUS_TSE`, `LEON_REG_UART_STATUS_THE`, `LEON_REG_UART_STATUS_BR`, `LEON_REG_UART_STATUS_OE`, `LEON_REG_UART_STATUS_PE`, `LEON_REG_UART_STATUS_FE`, `LEON_REG_UART_STATUS_ERR`, `LEON_REG_UART_CTRL_RE`, `LEON_REG_UART_CTRL_TE`, `LEON_REG_UART_CTRL_RI`, `LEON_REG_UART_CTRL_TI`, `LEON_REG_UART_CTRL_PS`, `LEON_REG_UART_CTRL_PE`, `LEON_REG_UART_CTRL_FL`, `LEON_REG_UART_CTRL_LB`, `LEON3_GPTIMER_EN`, `LEON3_GPTIMER_RL`, `LEON3_GPTIMER_LD`, `LEON3_GPTIMER_IRQEN`, `LEON3_GPTIMER_SEPIRQ`, `LEON3_GPTIMER_TIMERS`, and 97 more.

### Control Flow
LEON platform discovery scans AMBA configuration areas, records AHB/APB devices, maps IRQ controller and timer registers, and makes discovered devices available to early console, timer, IRQ, and driver setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global register pointers and AMBA device tables persist after discovery; timer and IRQ controller registers hold live hardware state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: device tree, LEON platform setup, APB/AHB device drivers, timer/IRQ code, and Gaisler vendor identifiers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect device-id or config-area decoding causes missing devices or wrong register maps; fixed table sizes can overflow if scanning is not bounded.

### Test Signals
LEON AMBA probe logs, timer/IRQ/serial operation, device tree population checks, and bounds testing for bus scan tables. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
