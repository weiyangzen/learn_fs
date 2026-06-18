# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.h

Purpose: Defines the shared R-Car PCIe register map, bit fields, constants, core data structure, access direction enum, and helper prototypes for R-Car PCIe controller code.

Important APIs/types/functions: The header defines `struct rcar_pcie { struct device *dev; void __iomem *base; }`, access constants `RCAR_PCI_ACCESS_READ` and `RCAR_PCI_ACCESS_WRITE`, MSI capacity `INT_PCI_MSI_NR`, resource/window limits, register address macros such as `PCIECAR`, `PCIECCTLR`, `PCIETCTLR`, `PCIETSTR`, `PCIEMSIFR`, `PCIELAR()`, `PCIEPALR()`, `PCICONF()`, and capability offset helpers `RCONF()`, `REXPCAP()`, and `RVCCAP()`.

Control flow: There is no executable flow. The macro definitions drive all register-level control in `pcie-rcar-host.c`, `pcie-rcar.c`, and endpoint support. Config access macros encode bus/device/function fields for controller PIO config cycles.

State and persistence: No state is allocated here. Constants describe persistent hardware register locations and bit meanings used by runtime code to initialize link state, MSI routing, config space, and memory windows.

Dependencies/integration: Depends on kernel bit macros and PCI structures included by users. It is tightly coupled with R-Car hardware manuals and the shared helper implementation in `pcie-rcar.c`.

Risks: Any incorrect offset or bit field corrupts controller programming across host and endpoint drivers. Window count constants (`MAX_NR_INBOUND_MAPS`, `RCAR_PCI_MAX_RESOURCES`) constrain resource parsing. Some macros encode legacy Gen1/Gen2/Gen3 behavior; new SoCs should not reuse them without register compatibility review.

Test signals: Build all R-Car PCIe variants, compare register definitions against vendor manuals, validate link training, MSI, config reads/writes, and resource windows on each compatible SoC generation.
