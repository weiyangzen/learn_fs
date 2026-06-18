<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/platform.c -->
# sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/platform.c

## Purpose
This ARC HSDK platform file performs early SoC setup for the Synopsys HS Development Kit. It programs the CREG memory bridge for CPU, RTT, AXI tunnel, HDMI, USB, Ethernet, SDIO, GPU, DMAC, and DVFS masters; reconciles DMAC coherency between a kernel data flag and the boot FDT; disables a problematic PAE remap path; raises the SDIO clock divider; configures GPIO interrupt pass-through; and registers the HSDK machine descriptor.

## Important APIs, Types, and Functions
Local functions/symbols include `Copyright`, `hsdk_enable_gpio_intc_wire`, `hsdk_tweak_node_coherency`, `HS`, `hsdk_init_memory_bridge`, `hsdk_init_early`. Important register or build constants include `ARC_CCM_UNUSED_ADDR`, `ARC_PERIPHERAL_BASE`, `CREG_BASE`, `SDIO_BASE`, `SDIO_UHS_REG_EXT`, `SDIO_UHS_REG_EXT_DIV_2`, `HSDK_GPIO_INTC`, `GPIO_INTEN`, `GPIO_INTMASK`, `GPIO_INTTYPE_LEVEL`, `GPIO_INT_POLARITY`, `GPIO_INT_CONNECTED_MASK`, `UPDATE_VAL`, `CREG_AXI_M_SLV0`, `CREG_AXI_M_SLV1`, `CREG_AXI_M_OFT0`, `CREG_AXI_M_OFT1`, `CREG_AXI_M_UPDT`, `CREG_AXI_M_HS_CORE_BOOT`, `CREG_PAE`, `CREG_PAE_UPDT`. Machine descriptor declarations are `SIMULATION` and notable compatible strings include `);
	return -EFAULT;
}

enum hsdk_axi_masters {
	M_HS_CORE = 0,
	M_HS_RTT,
	M_AXI_TUN,
	M_HDMI_VIDEO,
	M_HDMI_AUDIO,
	M_USB_HOST,
	M_ETHERNET,
	M_SDIO,
	M_GPU,
	M_DMAC_0,
	M_DMAC_1,
	M_DVFS
};

#define UPDATE_VAL	1

/*
 * This is modified configuration of AXI bridge. Default settings
 * are specified in `, `.
 *
 * AXI_M_m_SLV{0|1} - Slave Select register for master 'm'.
 * Possible slaves are:
 *  - 0  => no slave selected
 *  - 1  => DDR controller port #1
 *  - 2  => SRAM controller
 *  - 3  => AXI tunnel
 *  - 4  => EBI controller
 *  - 5  => ROM controller
 *  - 6  => AXI2APB bridge
 *  - 7  => DDR controller port #2
 *  - 8  => DDR controller port #3
 *  - 9  => HS38x4 IOC
 *  - 10 => HS38x4 DMI
 * AXI_M_m_OFFSET{0|1} - Addr Offset register for master 'm'
 *
 * Please read ARC HS Development IC Specification, section 17.2 for more
 * information about apertures configuration.
 *
 * m	master		AXI_M_m_SLV0	AXI_M_m_SLV1	AXI_M_m_OFFSET0	AXI_M_m_OFFSET1
 * 0	HS (CBU)	0x11111111	0x63111111	0xFEDCBA98	0x0E543210
 * 1	HS (RTT)	0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 2	AXI Tunnel	0x88888888	0x88888888	0xFEDCBA98	0x76543210
 * 3	HDMI-VIDEO	0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 4	HDMI-ADUIO	0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 5	USB-HOST	0x77777777	0x77999999	0xFEDCBA98	0x76DCBA98
 * 6	ETHERNET	0x77777777	0x77999999	0xFEDCBA98	0x76DCBA98
 * 7	SDIO		0x77777777	0x77999999	0xFEDCBA98	0x76DCBA98
 * 8	GPU		0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 9	DMAC (port #1)	0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 10	DMAC (port #2)	0x77777777	0x77777777	0xFEDCBA98	0x76543210
 * 11	DVFS		0x00000000	0x60000000	0x00000000	0x00000000
 */

#define CREG_AXI_M_SLV0(m)  ((void __iomem *)(CREG_BASE + 0x20 * (m)))
#define CREG_AXI_M_SLV1(m)  ((void __iomem *)(CREG_BASE + 0x20 * (m) + 0x04))
#define CREG_AXI_M_OFT0(m)  ((void __iomem *)(CREG_BASE + 0x20 * (m) + 0x08))
#define CREG_AXI_M_OFT1(m)  ((void __iomem *)(CREG_BASE + 0x20 * (m) + 0x0C))
#define CREG_AXI_M_UPDT(m)  ((void __iomem *)(CREG_BASE + 0x20 * (m) + 0x14))

#define CREG_AXI_M_HS_CORE_BOOT	((void __iomem *)(CREG_BASE + 0x010))

#define CREG_PAE		((void __iomem *)(CREG_BASE + 0x180))
#define CREG_PAE_UPDT		((void __iomem *)(CREG_BASE + 0x194))

static void __init hsdk_init_memory_bridge_axi_dmac(void)
{
	bool coherent = !!arc_hsdk_axi_dmac_coherent;
	u32 axi_m_slv1, axi_m_oft1;

	/*
	 * Don't tweak memory bridge configuration if we failed to tweak DTB
	 * as we will end up in a inconsistent state.
	 */
	if (hsdk_tweak_node_coherency(`, `, coherent))
		return;

	if (coherent) {
		axi_m_slv1 = 0x77999999;
		axi_m_oft1 = 0x76DCBA98;
	} else {
		axi_m_slv1 = 0x77777777;
		axi_m_oft1 = 0x76543210;
	}

	writel(0x77777777, CREG_AXI_M_SLV0(M_DMAC_0));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_DMAC_0));
	writel(axi_m_slv1, CREG_AXI_M_SLV1(M_DMAC_0));
	writel(axi_m_oft1, CREG_AXI_M_OFT1(M_DMAC_0));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_DMAC_0));

	writel(0x77777777, CREG_AXI_M_SLV0(M_DMAC_1));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_DMAC_1));
	writel(axi_m_slv1, CREG_AXI_M_SLV1(M_DMAC_1));
	writel(axi_m_oft1, CREG_AXI_M_OFT1(M_DMAC_1));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_DMAC_1));
}

static void __init hsdk_init_memory_bridge(void)
{
	u32 reg;

	/*
	 * M_HS_CORE has one unique register - BOOT.
	 * We need to clean boot mirror (BOOT[1:0]) bits in them to avoid first
	 * aperture to be masked by 'boot mirror'.
	 */
	reg = readl(CREG_AXI_M_HS_CORE_BOOT) & (~0x3);
	writel(reg, CREG_AXI_M_HS_CORE_BOOT);
	writel(0x11111111, CREG_AXI_M_SLV0(M_HS_CORE));
	writel(0x63111111, CREG_AXI_M_SLV1(M_HS_CORE));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_HS_CORE));
	writel(0x0E543210, CREG_AXI_M_OFT1(M_HS_CORE));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_HS_CORE));

	writel(0x77777777, CREG_AXI_M_SLV0(M_HS_RTT));
	writel(0x77777777, CREG_AXI_M_SLV1(M_HS_RTT));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_HS_RTT));
	writel(0x76543210, CREG_AXI_M_OFT1(M_HS_RTT));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_HS_RTT));

	writel(0x88888888, CREG_AXI_M_SLV0(M_AXI_TUN));
	writel(0x88888888, CREG_AXI_M_SLV1(M_AXI_TUN));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_AXI_TUN));
	writel(0x76543210, CREG_AXI_M_OFT1(M_AXI_TUN));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_AXI_TUN));

	writel(0x77777777, CREG_AXI_M_SLV0(M_HDMI_VIDEO));
	writel(0x77777777, CREG_AXI_M_SLV1(M_HDMI_VIDEO));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_HDMI_VIDEO));
	writel(0x76543210, CREG_AXI_M_OFT1(M_HDMI_VIDEO));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_HDMI_VIDEO));

	writel(0x77777777, CREG_AXI_M_SLV0(M_HDMI_AUDIO));
	writel(0x77777777, CREG_AXI_M_SLV1(M_HDMI_AUDIO));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_HDMI_AUDIO));
	writel(0x76543210, CREG_AXI_M_OFT1(M_HDMI_AUDIO));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_HDMI_AUDIO));

	writel(0x77777777, CREG_AXI_M_SLV0(M_USB_HOST));
	writel(0x77999999, CREG_AXI_M_SLV1(M_USB_HOST));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_USB_HOST));
	writel(0x76DCBA98, CREG_AXI_M_OFT1(M_USB_HOST));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_USB_HOST));

	writel(0x77777777, CREG_AXI_M_SLV0(M_ETHERNET));
	writel(0x77999999, CREG_AXI_M_SLV1(M_ETHERNET));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_ETHERNET));
	writel(0x76DCBA98, CREG_AXI_M_OFT1(M_ETHERNET));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_ETHERNET));

	writel(0x77777777, CREG_AXI_M_SLV0(M_SDIO));
	writel(0x77999999, CREG_AXI_M_SLV1(M_SDIO));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_SDIO));
	writel(0x76DCBA98, CREG_AXI_M_OFT1(M_SDIO));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_SDIO));

	writel(0x77777777, CREG_AXI_M_SLV0(M_GPU));
	writel(0x77777777, CREG_AXI_M_SLV1(M_GPU));
	writel(0xFEDCBA98, CREG_AXI_M_OFT0(M_GPU));
	writel(0x76543210, CREG_AXI_M_OFT1(M_GPU));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_GPU));

	writel(0x00000000, CREG_AXI_M_SLV0(M_DVFS));
	writel(0x60000000, CREG_AXI_M_SLV1(M_DVFS));
	writel(0x00000000, CREG_AXI_M_OFT0(M_DVFS));
	writel(0x00000000, CREG_AXI_M_OFT1(M_DVFS));
	writel(UPDATE_VAL, CREG_AXI_M_UPDT(M_DVFS));

	hsdk_init_memory_bridge_axi_dmac();

	/*
	 * PAE remapping for DMA clients does not work due to an RTL bug, so
	 * CREG_PAE register must be programmed to all zeroes, otherwise it
	 * will cause problems with DMA to/from peripherals even if PAE40 is
	 * not used.
	 */
	writel(0x00000000, CREG_PAE);
	writel(UPDATE_VAL, CREG_PAE_UPDT);
}

static void __init hsdk_init_early(void)
{
	hsdk_init_memory_bridge();

	/*
	 * Switch SDIO external ciu clock divider from default div-by-8 to
	 * minimum possible div-by-2.
	 */
	iowrite32(SDIO_UHS_REG_EXT_DIV_2, (void __iomem *) SDIO_UHS_REG_EXT);

	hsdk_enable_gpio_intc_wire();
}

static const char *hsdk_compat[] __initconst = {
	`, `,
	NULL,
};

MACHINE_START(SIMULATION, `.

## Control Flow
`hsdk_init_early()` calls `hsdk_init_memory_bridge()`, adjusts the SDIO UHS divider, and enables the GPIO interrupt wire. The memory-bridge routine writes slave select, offset, and update registers for each AXI master, clears HS core boot mirror bits, calls `hsdk_init_memory_bridge_axi_dmac()` for coherent/non-coherent DMAC mapping, and finally zeros PAE registers due to an RTL bug. `hsdk_tweak_node_coherency()` edits `/soc/dmac@80000` in `initial_boot_params` so the DT `dma-coherent` property matches the selected AXI path before drivers probe.

## State and Persistence Behavior
The code persists no filesystem state. It mutates early hardware registers through raw MMIO and, on HSDK/AXS103 paths, may mutate the in-memory flattened device tree before normal device creation. Those writes shape later driver-visible interrupt topology, DMA coherency, memory aperture routing, clock rates, and peripheral reset state. The effects persist until reset or later platform/driver reconfiguration.

## Dependencies and Integration Points
Dependencies include ARC machine descriptor infrastructure, `initial_boot_params`, libfdt helpers where FDT patching is used, ARC auxiliary register access, `ioread32`/`iowrite32`/`readl`/`writel`, platform DTS compatible strings, and interrupt/GPIO/clock/reset drivers that assume this early wiring. Integration is with `arch/arc` boot selection and board-specific DTS files.

## Risks
Risks are incorrect physical register addresses, changing interrupt topology before the irqchip stack is initialized, FDT patch failures that leave hardware and DT in different coherency or clock states, endian-sensitive bitfield decoding of FPGA version registers, and platform-specific magic constants that are hard to validate without the board or simulator. For HSDK, the DMAC coherency flag and PAE workaround are particularly sensitive because later DMA failures can appear far from early boot.

## Test Signals
Build the relevant ARC defconfig with the platform option enabled, boot matching DTS files on hardware or simulator, and inspect early `pr_info`/`pr_err` messages plus interrupt, UART, Ethernet, SDIO, USB, and DMA behavior. DTS validation should include the compatible strings registered here. Regression tests should cover SMP/quad AXS103, coherent and non-coherent HSDK DMAC modes, and absence of spurious nested interrupt-controller probe failures.

Source read size: 326 lines, 10709 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/platform.c -->
