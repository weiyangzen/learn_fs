<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/axs10x.c -->
# sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/axs10x.c

## Purpose
This ARC platform file provides early board support for Synopsys AXS101 and AXS103 development systems. It programs motherboard and CPU-card CREG/GPIO registers, configures interrupt pass-through wiring, adjusts AXI aperture maps for AXS101, optionally patches AXS103 quad-core clock data in the boot FDT, prints FPGA build dates, and registers `MACHINE_START` entries for the matching DT compatibles.

## Important APIs, Types, and Functions
Local functions/symbols include `Copyright`, `axs10x_print_board_ver`, `axs10x_early_init`, `Master`, `axs101_set_memmap`, `axs101_early_init`, `axs103_early_init`. Important register or build constants include `AXS_MB_CGU`, `AXS_MB_CREG`, `CREG_MB_IRQ_MUX`, `CREG_MB_SW_RESET`, `CREG_MB_VER`, `CREG_MB_CONFIG`, `AXC001_CREG`, `AXC001_GPIO_INTC`, `GPIO_INTEN`, `GPIO_INTMASK`, `GPIO_INTTYPE_LEVEL`, `GPIO_INT_POLARITY`, `MB_TO_GPIO_IRQ`, `CREG_CPU_ADDR_770`, `CREG_CPU_ADDR_TUNN`, `CREG_CPU_ADDR_770_UPD`, `CREG_CPU_ADDR_TUNN_UPD`, `CREG_CPU_ARC770_IRQ_MUX`, `CREG_CPU_GPIO_UART_MUX`, `AXC001_SLV_NONE`, `AXC001_SLV_DDR_PORT0`, `AXC001_SLV_SRAM`, `AXC001_SLV_AXI_TUNNEL`, `AXC001_SLV_AXI2APB`, and 14 more. Machine descriptor declarations are `AXS101`, `AXS103` and notable compatible strings include `snps,axs101`, `snps,axs103`.

## Control Flow
`axs101_early_init()` builds the ARC770 and tunnel memory maps, updates motherboard peripheral aperture registers, selects GPIO/UART muxing, resets Ethernet/ULPI, remaps interrupts, and then calls common AXS10x early setup. `axs103_early_init()` optionally lowers the quad-core core clock by editing `/cpu_card/core_clk` in the in-memory FDT, configures UART/tunnel I/O, connects motherboard interrupts, prints CPU-card version data, and then runs common setup. `axs10x_enable_gpio_intc_wire()` programs the DW APB GPIO block as a pass-through interrupt wire so the real motherboard interrupt controller can be represented directly to the CPU interrupt controller.

## State and Persistence Behavior
The code persists no filesystem state. It mutates early hardware registers through raw MMIO and, on HSDK/AXS103 paths, may mutate the in-memory flattened device tree before normal device creation. Those writes shape later driver-visible interrupt topology, DMA coherency, memory aperture routing, clock rates, and peripheral reset state. The effects persist until reset or later platform/driver reconfiguration.

## Dependencies and Integration Points
Dependencies include ARC machine descriptor infrastructure, `initial_boot_params`, libfdt helpers where FDT patching is used, ARC auxiliary register access, `ioread32`/`iowrite32`/`readl`/`writel`, platform DTS compatible strings, and interrupt/GPIO/clock/reset drivers that assume this early wiring. Integration is with `arch/arc` boot selection and board-specific DTS files.

## Risks
Risks are incorrect physical register addresses, changing interrupt topology before the irqchip stack is initialized, FDT patch failures that leave hardware and DT in different coherency or clock states, endian-sensitive bitfield decoding of FPGA version registers, and platform-specific magic constants that are hard to validate without the board or simulator. For HSDK, the DMAC coherency flag and PAE workaround are particularly sensitive because later DMA failures can appear far from early boot.

## Test Signals
Build the relevant ARC defconfig with the platform option enabled, boot matching DTS files on hardware or simulator, and inspect early `pr_info`/`pr_err` messages plus interrupt, UART, Ethernet, SDIO, USB, and DMA behavior. DTS validation should include the compatible strings registered here. Regression tests should cover SMP/quad AXS103, coherent and non-coherent HSDK DMAC modes, and absence of spurious nested interrupt-controller probe failures.

Source read size: 384 lines, 11398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/axs10x.c -->
