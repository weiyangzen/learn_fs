<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-sim/platform.c -->
# sources/distributed-fs/ceph-client/arch/arc/plat-sim/platform.c

## Purpose
This small ARC platform file registers a Device Tree matched machine descriptor for the platform. It supplies compatible strings and lets common ARC boot code select the platform callback table during early DT scanning.

## Important APIs, Types, and Functions
Local functions/symbols include `Copyright`. Important register or build constants include none. Machine descriptor declarations are `SIMULATION` and notable compatible strings include `snps,nsim`, `snps,nsimosci`, `snps,nsimosci_hs`, `snps,zebu_hs`.

## Control Flow
There is no custom early hardware programming. Boot-time control flow is DT compatible matching against the local string table followed by generic ARC machine setup through the `MACHINE_START` descriptor.

## State and Persistence Behavior
The code persists no filesystem state. It mutates early hardware registers through raw MMIO and, on HSDK/AXS103 paths, may mutate the in-memory flattened device tree before normal device creation. Those writes shape later driver-visible interrupt topology, DMA coherency, memory aperture routing, clock rates, and peripheral reset state. The effects persist until reset or later platform/driver reconfiguration.

## Dependencies and Integration Points
Dependencies include ARC machine descriptor infrastructure, `initial_boot_params`, libfdt helpers where FDT patching is used, ARC auxiliary register access, `ioread32`/`iowrite32`/`readl`/`writel`, platform DTS compatible strings, and interrupt/GPIO/clock/reset drivers that assume this early wiring. Integration is with `arch/arc` boot selection and board-specific DTS files.

## Risks
Risks are incorrect physical register addresses, changing interrupt topology before the irqchip stack is initialized, FDT patch failures that leave hardware and DT in different coherency or clock states, endian-sensitive bitfield decoding of FPGA version registers, and platform-specific magic constants that are hard to validate without the board or simulator. For HSDK, the DMAC coherency flag and PAE workaround are particularly sensitive because later DMA failures can appear far from early boot.

## Test Signals
Build the relevant ARC defconfig with the platform option enabled, boot matching DTS files on hardware or simulator, and inspect early `pr_info`/`pr_err` messages plus interrupt, UART, Ethernet, SDIO, USB, and DMA behavior. DTS validation should include the compatible strings registered here. Regression tests should cover SMP/quad AXS103, coherent and non-coherent HSDK DMAC modes, and absence of spurious nested interrupt-controller probe failures.

Source read size: 32 lines, 825 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-sim/platform.c -->
