# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar71xx_regs.h

**Purpose:** This is the central ATH79 register map header for Atheros/QCA AR71xx, AR724x, AR913x, AR933x, AR934x, QCA953x, QCA955x, QCA956x, and related SoCs. It gives board code and platform drivers stable symbolic names for physical MMIO bases, block sizes, register offsets, bit fields, reset lines, bootstrap pins, interrupt status masks, revision IDs, GPIO mux selectors, SPI signals, MII/GMAC mode fields, PCI/PCIe windows, USB, DDR flush registers, PLL controls, and hidden QCA956x MAC/DAM configuration registers.

**Important APIs/types/functions:** The public surface is almost entirely `#define` constants. Major groups include `AR71XX_APB_BASE`, per-block base/size pairs, PCI window offsets, DDR flush offsets, PLL register fields, reset-module bits, bootstrap bits, `REV_ID_*` masks, SPI register bits, GPIO register and mux values, MII control fields, and GMAC/SGMII configuration masks. It includes `<linux/types.h>`, `<linux/io.h>`, and `<linux/bitops.h>` for typed MMIO consumers and `BIT()` masks, but declares no functions.

**Control flow:** The header has no runtime flow by itself. Its constants drive control flow in platform init, clock, reset, PCI, GPIO, Ethernet, SPI, USB, and interrupt code that selects SoC-specific offsets after CPU revision detection, reads/writes MMIO registers, and composes bit masks for hardware sequencing. Macros such as `AR934X_PCIE_WMAC_INT_*_ALL` and `QCA955X_EXT_INT_*_ALL` encode grouped interrupt handling policy.

**State and persistence behavior:** It owns no C storage. Consumers mutate persistent hardware state by writing reset, PLL, GPIO mux, PCI window, SPI, DDR flush, and GMAC registers named here. Many values are boot-time strap or revision IDs and must be treated as hardware ABI, not ordinary configurable state.

**Dependencies and integration points:** Integrated by ATH79 arch setup, clock/reset code, PCI/PCIe host setup, GPIO/pinctrl users, Ethernet MAC/SGMII setup, SPI flash access, USB platform devices, and interrupt controllers. It depends on `BIT()` and raw MMIO helpers in consumers.

**Risks:** The file is dense and SoC variants reuse similar register names with different offsets or bit meanings. A wrong base, size, reset bit, or mux value can hang boot, break flash access, disable Ethernet/USB/PCIe, or corrupt DDR/flush handling. Unsupported hardware placeholders are not explicit, so incorrect variant selection is a key risk. Some hidden QCA956x addresses are outside the normal APB base and need extra care.

**Test signals:** Build ATH79 defconfigs with PCI, Ethernet, SPI, GPIO, and USB enabled. Boot-test each supported SoC family, checking revision detection, DDR write-buffer flushes, reset sequencing, GPIO muxing, SPI flash probe, PCIe enumeration, Ethernet link modes, USB enumeration, and interrupt delivery. Static review should compare every offset and bit with datasheets and downstream BSP users.
