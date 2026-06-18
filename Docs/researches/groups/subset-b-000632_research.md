# subset-b-000632 Research

Grouped source research for ARC platform/JIT support and ARM boot/build infrastructure under the Ceph client source tree. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_core.c -->
# sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_core.c

## Purpose
This file is the architecture-neutral orchestration layer for the ARC eBPF JIT. It translates verifier-approved `struct bpf_prog` instructions into ARC machine code by coordinating a backend declared in `bpf_jit.h`, allocating executable BPF JIT memory, tracking BPF-to-native instruction offsets, and handling the normal pass plus the extra relocation pass needed for BPF subprogram calls and pseudo-function immediates.

## Important APIs, Types, and Functions
Key local data structures are `struct jit_buffer`, `struct arc_jit_data`, and `struct jit_context`. Important helpers include `dump_bytes`, `vm_dump`, `jit_dump`, `jit_ctx_init`, `pass`, `maybe_free`, `jit_ctx_cleanup`, `analyze_reg_usage`, `jit_buffer_check`, `jit_buffer_update`, `handle_prologue`, `handle_epilogue`, `get_index_for_insn`, `get_offset`, `get_target_index_for_insn`, `has_imm`, `is_last_insn`, `set_need_for_extra_pass`, `handle_swap`, `check_insn_idx_valid`, `bpf_cond_to_arc`, `check_bpf_jump`, `index`, `feasible_jit_jump`, `handle_jumps`, `handle_jmp_epilogue`, `handle_call`, `handle_ld_imm64`, `handle_insn`, `handle_body`, `fill_ill_insn`, `jit_prepare_early_mem_alloc`, `jit_prepare`, `jit_compile`, and 5 more. `CHECK_RET` provides the common early-return pattern. The backend API surface is reached through calls such as `arc_prologue`, `arc_epilogue`, `mask_for_used_regs`, `gen_jmp_32`, `gen_jmp_64`, `gen_func_call`, register move/ALU/load/store emitters, and branch feasibility checks. Kernel BPF integration goes through `bpf_int_jit_compile`, `bpf_jit_binary_alloc`, `bpf_jit_binary_lock_ro`, `bpf_jit_get_func_addr`, `bpf_prog_fill_jited_linfo`, and `flush_icache_range`. Local preprocessor symbols include `CHECK_RET`.

## Control Flow
`bpf_int_jit_compile()` dumps the input under debug and chooses a normal pass for a non-jitted program or an extra pass when the BPF core invokes the JIT again after subprogram addresses become known. The normal pass initializes `jit_context`, performs a dry run in `jit_prepare()` to analyze register use, emit virtual prologue/body/epilogue lengths, populate `bpf2insn`, compute `epilogue_offset`, and allocate a JIT image prefilled with illegal ARC instructions. `jit_compile()` then repeats prologue, body, and epilogue emission into the allocated buffer and verifies byte count convergence. `handle_insn()` is the opcode dispatcher for 32-bit and 64-bit ALU, endian swaps, loads, stores, conditional/unconditional jumps, calls, exit, and 64-bit immediate loads. Jumps are validated against BPF indices and then backend native offsets once the dry-run map is available. Calls and pseudo-function `ldimm64` instructions set `need_extra_pass` when target addresses are not yet fixed. The extra pass resumes `prog->aux->jit_data`, rewrites only call and `ldimm64` sites at their existing offsets, then finalizes the image again.

## State and Persistence Behavior
The persistent handoff is `prog->bpf_func`, `prog->jited_len`, `prog->jited`, and optional `prog->aux->jit_data`. `bpf2insn` maps verifier instruction indices to native offsets for line-info, jumps, and relocation patching. `arc_jit_data` intentionally survives the first pass only when an extra pass is forecast; otherwise cleanup frees transient arrays and locks the binary header read-only/executable. Failure cleanup frees the binary header and clears partially installed `bpf_func` state for extra-pass failures. Runtime code is not persisted beyond kernel memory and is reclaimed later by generic BPF JIT free paths using `bpf_jit_binary_hdr()`.

## Dependencies and Integration Points
This source depends on Linux BPF core types, ARC backend emitters from `bpf_jit.h`, kernel allocation APIs, executable memory locking, instruction-cache flushing, verifier metadata such as `verifier_zext`, `stack_depth`, `is_func`, and global `bpf_jit_enable` debugging. Integration points include JIT subprogram relocation in the verifier, BPF line-info filling, ARC instruction encoding helpers, the architecture register convention, and the generic BPF program lifecycle.

## Risks
The high-risk areas are dry-run/emission divergence, incorrect `bpf2insn` offsets for two-slot `ldimm64`, branch displacement feasibility, stale relocation patching during the extra pass, zero-extension mismatches when the verifier does not provide zext, and cleanup paths that could leak or prematurely free `jit_data`. Generated code correctness also depends on backend helpers honoring the same length accounting in dry-run and emit modes. A bad branch or call address can create executable memory corruption or runtime traps, while a missing illegal-instruction fill weakens fault isolation around unused bytes.

## Test Signals
Useful signals are ARC eBPF selftests from `tools/testing/selftests/bpf`, verifier programs containing subprogram calls, pseudo-function `ldimm64`, forward/backward jumps, `BPF_JMP32 | BPF_JA`, endian swaps, signed memory loads, and 32-bit ALU operations that require zero-extension. Enable `bpf_jit_enable` and, where built, `ARC_BPF_JIT_DEBUG` to compare VM bytes and JIT bytes. Negative testing should force unsupported opcodes and branch ranges to confirm graceful fallback without leaving `prog->jited` or executable memory in an inconsistent state.

Source read size: 1414 lines, 37892 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Kconfig

## Purpose
This platform Kconfig file declares ARC platform selection for `plat-axs10x` and gates the platform objects and dependent drivers used by the ARC build.

## Important APIs, Types, and Functions
Exported Kconfig symbols are `ARC_PLAT_AXS10X`, `AXS101`, `AXS103`. They select `DW_APB_ICTL`, `GPIO_DWAPB`, `HAVE_PCI`, `GENERIC_IRQ_CHIP`, `GPIOLIB`, `AXS101`, `AXS103` and depend on `ISA_ARCOMPACT`, `ISA_ARCV2`.

## Control Flow
During Kconfig resolution, selecting the menuconfig enables the platform symbol, pulls in selected irqchip/GPIO/clock/reset/pinctrl support, and lets the platform Makefile compile the corresponding early machine descriptor. Child symbols choose CPU-card variants where present.

## State and Persistence Behavior
Kconfig files do not mutate runtime state. Their persistent output is the generated `.config` and derived headers such as `include/generated/autoconf.h`, which control compilation, linked objects, linker flags, and runtime code paths until the next configuration run.

## Dependencies and Integration Points
Dependencies and integration points include selected symbols `DW_APB_ICTL`, `GPIO_DWAPB`, `HAVE_PCI`, `GENERIC_IRQ_CHIP`, `GPIOLIB`, `AXS101`, `AXS103`, dependency expressions `ISA_ARCOMPACT`, `ISA_ARCV2`, sourced Kconfig files none, architecture Makefiles, board DTS choices, and drivers enabled by the selected platform capabilities.

## Risks
Risks include overusing `select` to force symbols whose dependencies are not met, missing dependency guards for CPU ISA or MMU assumptions, hidden build breakage when sourced Kconfig files move, and configuration combinations that compile a platform without the DT or driver support required to boot it.

## Test Signals
Run `make ARCH=arc olddefconfig` or `make ARCH=arm olddefconfig` for affected defconfigs, `make ARCH=... savedefconfig` to detect unintended symbol churn, and build representative platform defconfigs. For `arch/arm/Kconfig`, also test `multi_v7_defconfig`, NOMMU/v7-M configurations, and selected errata combinations.

Source read size: 45 lines, 1251 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Makefile

## Purpose
This Makefile wires `sources/distributed-fs/ceph-client/arch/arc/plat-axs10x` into the kernel build by adding platform or architecture objects/subdirectories under the appropriate Kbuild variables.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `obj-$(CONFIG_ARC_PLAT_AXS10X)`. Conditional gates include `CONFIG_ARC_PLAT_AXS10X`.

## Control Flow
Kbuild evaluates the assignments after Kconfig resolution and appends the listed objects or subdirectories to the architecture build. Conditional `obj-$(CONFIG_...)` entries compile only when the matching platform symbol is enabled.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are unconditional objects in the wrong build scope, missing include paths, stale object names, and Kconfig symbols not matching the source dependencies.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 6 lines, 145 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-axs10x/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig

## Purpose
This platform Kconfig file declares ARC platform selection for `plat-hsdk` and gates the platform objects and dependent drivers used by the ARC build.

## Important APIs, Types, and Functions
Exported Kconfig symbols are `ARC_SOC_HSDK`. They select `ARC_HAS_ACCL_REGS`, `ARC_IRQ_NO_AUTOSAVE`, `ARC_FPU_SAVE_RESTORE`, `CLK_HSDK`, `RESET_CONTROLLER`, `RESET_HSDK`, `HAVE_PCI` and depend on `ISA_ARCV2`.

## Control Flow
During Kconfig resolution, selecting the menuconfig enables the platform symbol, pulls in selected irqchip/GPIO/clock/reset/pinctrl support, and lets the platform Makefile compile the corresponding early machine descriptor. Child symbols choose CPU-card variants where present.

## State and Persistence Behavior
Kconfig files do not mutate runtime state. Their persistent output is the generated `.config` and derived headers such as `include/generated/autoconf.h`, which control compilation, linked objects, linker flags, and runtime code paths until the next configuration run.

## Dependencies and Integration Points
Dependencies and integration points include selected symbols `ARC_HAS_ACCL_REGS`, `ARC_IRQ_NO_AUTOSAVE`, `ARC_FPU_SAVE_RESTORE`, `CLK_HSDK`, `RESET_CONTROLLER`, `RESET_HSDK`, `HAVE_PCI`, dependency expressions `ISA_ARCV2`, sourced Kconfig files none, architecture Makefiles, board DTS choices, and drivers enabled by the selected platform capabilities.

## Risks
Risks include overusing `select` to force symbols whose dependencies are not met, missing dependency guards for CPU ISA or MMU assumptions, hidden build breakage when sourced Kconfig files move, and configuration combinations that compile a platform without the DT or driver support required to boot it.

## Test Signals
Run `make ARCH=arc olddefconfig` or `make ARCH=arm olddefconfig` for affected defconfigs, `make ARCH=... savedefconfig` to detect unintended symbol churn, and build representative platform defconfigs. For `arch/arm/Kconfig`, also test `multi_v7_defconfig`, NOMMU/v7-M configurations, and selected errata combinations.

Source read size: 14 lines, 340 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Makefile

## Purpose
This Makefile wires `sources/distributed-fs/ceph-client/arch/arc/plat-hsdk` into the kernel build by adding platform or architecture objects/subdirectories under the appropriate Kbuild variables.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `obj-y`. Conditional gates include none.

## Control Flow
Kbuild evaluates the assignments after Kconfig resolution and appends the listed objects or subdirectories to the architecture build. Conditional `obj-$(CONFIG_...)` entries compile only when the matching platform symbol is enabled.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are unconditional objects in the wrong build scope, missing include paths, stale object names, and Kconfig symbols not matching the source dependencies.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 6 lines, 120 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-sim/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/plat-sim/Makefile

## Purpose
This Makefile wires `sources/distributed-fs/ceph-client/arch/arc/plat-sim` into the kernel build by adding platform or architecture objects/subdirectories under the appropriate Kbuild variables.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `obj-y`. Conditional gates include none.

## Control Flow
Kbuild evaluates the assignments after Kconfig resolution and appends the listed objects or subdirectories to the architecture build. Conditional `obj-$(CONFIG_...)` entries compile only when the matching platform symbol is enabled.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are unconditional objects in the wrong build scope, missing include paths, stale object names, and Kconfig symbols not matching the source dependencies.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 6 lines, 125 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-sim/Makefile -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Kconfig

## Purpose
This platform Kconfig file declares ARC platform selection for `plat-tb10x` and gates the platform objects and dependent drivers used by the ARC build.

## Important APIs, Types, and Functions
Exported Kconfig symbols are `ARC_PLAT_TB10X`. They select `PINCTRL`, `PINCTRL_TB10X`, `PINMUX`, `GPIOLIB`, `GPIO_TB10X`, `TB10X_IRQC` and depend on none.

## Control Flow
During Kconfig resolution, selecting the menuconfig enables the platform symbol, pulls in selected irqchip/GPIO/clock/reset/pinctrl support, and lets the platform Makefile compile the corresponding early machine descriptor. Child symbols choose CPU-card variants where present.

## State and Persistence Behavior
Kconfig files do not mutate runtime state. Their persistent output is the generated `.config` and derived headers such as `include/generated/autoconf.h`, which control compilation, linked objects, linker flags, and runtime code paths until the next configuration run.

## Dependencies and Integration Points
Dependencies and integration points include selected symbols `PINCTRL`, `PINCTRL_TB10X`, `PINMUX`, `GPIOLIB`, `GPIO_TB10X`, `TB10X_IRQC`, dependency expressions none, sourced Kconfig files none, architecture Makefiles, board DTS choices, and drivers enabled by the selected platform capabilities.

## Risks
Risks include overusing `select` to force symbols whose dependencies are not met, missing dependency guards for CPU ISA or MMU assumptions, hidden build breakage when sourced Kconfig files move, and configuration combinations that compile a platform without the DT or driver support required to boot it.

## Test Signals
Run `make ARCH=arc olddefconfig` or `make ARCH=arm olddefconfig` for affected defconfigs, `make ARCH=... savedefconfig` to detect unintended symbol churn, and build representative platform defconfigs. For `arch/arm/Kconfig`, also test `multi_v7_defconfig`, NOMMU/v7-M configurations, and selected errata combinations.

Source read size: 20 lines, 577 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Makefile

## Purpose
This Makefile wires `sources/distributed-fs/ceph-client/arch/arc/plat-tb10x` into the kernel build by adding platform or architecture objects/subdirectories under the appropriate Kbuild variables.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `KBUILD_CFLAGS`, `obj-y`. Conditional gates include none.

## Control Flow
Kbuild evaluates the assignments after Kconfig resolution and appends the listed objects or subdirectories to the architecture build. Conditional `obj-$(CONFIG_...)` entries compile only when the matching platform symbol is enabled.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are unconditional objects in the wrong build scope, missing include paths, stale object names, and Kconfig symbols not matching the source dependencies.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 10 lines, 213 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/tb10x.c -->
# sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/tb10x.c

## Purpose
This small ARC platform file registers a Device Tree matched machine descriptor for the platform. It supplies compatible strings and lets common ARC boot code select the platform callback table during early DT scanning.

## Important APIs, Types, and Functions
Local functions/symbols include none. Important register or build constants include none. Machine descriptor declarations are `TB10x` and notable compatible strings include `abilis,arc-tb10x`.

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

Source read size: 20 lines, 403 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-tb10x/tb10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arm/Kbuild

## Purpose
This Makefile wires `sources/distributed-fs/ceph-client/arch/arm` into the kernel build by adding platform or architecture objects/subdirectories under the appropriate Kbuild variables.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `obj-$(CONFIG_FPE_NWFPE)`, `obj-$(CONFIG_FPE_FASTFPE)`, `obj-$(CONFIG_VFP)`, `obj-$(CONFIG_XEN)`, `obj-$(CONFIG_VDSO)`, `obj-y`, `subdir-`. Conditional gates include `CONFIG_FPE_NWFPE`, `CONFIG_FPE_FASTFPE`, `CONFIG_VFP`, `CONFIG_XEN`, `CONFIG_VDSO`.

## Control Flow
Kbuild evaluates the assignments after Kconfig resolution and appends the listed objects or subdirectories to the architecture build. Conditional `obj-$(CONFIG_...)` entries compile only when the matching platform symbol is enabled.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are unconditional objects in the wrong build scope, missing include paths, stale object names, and Kconfig symbols not matching the source dependencies.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 14 lines, 396 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/Kconfig

## Purpose
This is the top-level Kconfig contract for 32-bit ARM Linux. It declares `config ARM`, selects architecture-wide kernel capabilities, defines MMU/multiplatform/physical-memory options, sources every ARM machine/platform Kconfig subtree, and exposes CPU errata and subsystem feature knobs that determine build-time architecture behavior.

## Important APIs, Types, and Functions
Primary symbols include `ARM`, `ARM_HAS_GROUP_RELOCS`, `ARM_DMA_USE_IOMMU`, `ARM_DMA_IOMMU_ALIGNMENT`, `SYS_SUPPORTS_APM_EMULATION`, `HAVE_TCM`, `HAVE_PROC_CPU`, `NO_IOPORT_MAP`, `SBUS`, `STACKTRACE_SUPPORT`, `LOCKDEP_SUPPORT`, `ARCH_HAS_ILOG2_U32`, `ARCH_HAS_ILOG2_U64`, `ARCH_HAS_BANDGAP`, `FIX_EARLYCON_MEM`, `GENERIC_HWEIGHT`, `GENERIC_CALIBRATE_DELAY`, `ARCH_MAY_HAVE_PC_FDC`, `ARCH_SUPPORTS_UPROBES`, `GENERIC_ISA_DMA`, `FIQ`, `ARCH_MTD_XIP`, `ARM_PATCH_PHYS_VIRT`, `NEED_MACH_IO_H`, `NEED_MACH_MEMORY_H`, `PHYS_OFFSET`, `GENERIC_BUG`, `PGTABLE_LEVELS`, `MMU`, `ARM_SINGLE_ARMV7M`, `ARCH_MMAP_RND_BITS_MIN`, `ARCH_MMAP_RND_BITS_MAX`, `ARCH_MULTIPLATFORM`, `ARCH_LPC18XX`, and 125 more. The top-level `ARM` symbol selects a large capability set including BPF JIT support, DMA APIs, MMU helpers, tracing/probing support, seccomp, VDSO/Rust eligibility, and OF early flattree support. It sources 61 subordinate Kconfig files, including `arch/arm/Kconfig.platforms`, `arch/arm/mach-actions/Kconfig`, `arch/arm/mach-alpine/Kconfig`, `arch/arm/mach-artpec/Kconfig`, `arch/arm/mach-aspeed/Kconfig`, `arch/arm/mach-at91/Kconfig`, `arch/arm/mach-axxia/Kconfig`, `arch/arm/mach-bcm/Kconfig`, `arch/arm/mach-berlin/Kconfig`, `arch/arm/mach-clps711x/Kconfig`, `arch/arm/mach-davinci/Kconfig`, `arch/arm/mach-digicolor/Kconfig`, `arch/arm/mach-dove/Kconfig`, `arch/arm/mach-ep93xx/Kconfig`, `arch/arm/mach-exynos/Kconfig`, `arch/arm/mach-footbridge/Kconfig`, `arch/arm/mach-gemini/Kconfig`, `arch/arm/mach-highbank/Kconfig`, and 43 more.

## Control Flow
Kconfig evaluation starts at `config ARM`, applies defaults and `select` dependencies, enters the System Type menu, optionally enables single ARMv7-M or multiplatform behavior, then loads all machine Kconfig files and the ARM MMU/NOMMU and errata menus. The selected symbols later control `arch/arm/Makefile`, machine directory inclusion, decompressor options, DMA/MMU code, tracing, and driver availability.

## State and Persistence Behavior
Kconfig files do not mutate runtime state. Their persistent output is the generated `.config` and derived headers such as `include/generated/autoconf.h`, which control compilation, linked objects, linker flags, and runtime code paths until the next configuration run.

## Dependencies and Integration Points
Dependencies and integration points include selected symbols `ARCH_32BIT_OFF_T`, `ARCH_CORRECT_STACKTRACE_ON_KRETPROBE`, `ARCH_HAS_BINFMT_FLAT`, `ARCH_HAS_CACHE_LINE_SIZE`, `ARCH_HAS_CC_CAN_LINK`, `ARCH_HAS_CPU_CACHE_ALIASING`, `ARCH_HAS_CPU_FINALIZE_INIT`, `ARCH_HAS_CURRENT_STACK_POINTER`, `ARCH_HAS_DEBUG_VIRTUAL`, `ARCH_HAS_DMA_ALLOC`, `ARCH_HAS_DMA_OPS`, `ARCH_HAS_DMA_WRITE_COMBINE`, `ARCH_HAS_ELF_RANDOMIZE`, `ARCH_HAS_FORTIFY_SOURCE`, `ARCH_HAS_KEEPINITRD`, `ARCH_HAS_KCOV`, `ARCH_HAS_MEMBARRIER_SYNC_CORE`, `ARCH_HAS_NON_OVERLAPPING_ADDRESS_SPACE`, `ARCH_HAS_PTE_SPECIAL`, `ARCH_HAS_SETUP_DMA_OPS`, `ARCH_HAS_SET_MEMORY`, `ARCH_STACKWALK`, `ARCH_HAS_STRICT_KERNEL_RWX`, `ARCH_HAS_STRICT_MODULE_RWX`, and 174 more, dependency expressions `MMU`, `!ARM_PATCH_PHYS_VIRT || !AUTO_ZRELADDR`, `BUG`, `MMU && !(ARCH_FOOTBRIDGE || ARCH_RPC || ARCH_SA1100)`, `ARM_SINGLE_ARMV7M`, `CPU_XSCALE || CPU_XSC3 || CPU_MOHAWK`, `CPU_PJ4B && MACH_ARMADA_370`, `CPU_V6`, `CPU_V6 || CPU_V6K`, `CPU_V7`, `!ARCH_MULTIPLATFORM`, `CPU_V7 && SMP`, and 50 more, sourced Kconfig files `arch/arm/Kconfig.platforms`, `arch/arm/mach-actions/Kconfig`, `arch/arm/mach-alpine/Kconfig`, `arch/arm/mach-artpec/Kconfig`, `arch/arm/mach-aspeed/Kconfig`, `arch/arm/mach-at91/Kconfig`, `arch/arm/mach-axxia/Kconfig`, `arch/arm/mach-bcm/Kconfig`, `arch/arm/mach-berlin/Kconfig`, `arch/arm/mach-clps711x/Kconfig`, `arch/arm/mach-davinci/Kconfig`, `arch/arm/mach-digicolor/Kconfig`, `arch/arm/mach-dove/Kconfig`, `arch/arm/mach-ep93xx/Kconfig`, `arch/arm/mach-exynos/Kconfig`, `arch/arm/mach-footbridge/Kconfig`, `arch/arm/mach-gemini/Kconfig`, `arch/arm/mach-highbank/Kconfig`, `arch/arm/mach-hisi/Kconfig`, `arch/arm/mach-imx/Kconfig`, and 41 more, architecture Makefiles, board DTS choices, and drivers enabled by the selected platform capabilities.

## Risks
Risks include overusing `select` to force symbols whose dependencies are not met, missing dependency guards for CPU ISA or MMU assumptions, hidden build breakage when sourced Kconfig files move, and configuration combinations that compile a platform without the DT or driver support required to boot it.

## Test Signals
Run `make ARCH=arc olddefconfig` or `make ARCH=arm olddefconfig` for affected defconfigs, `make ARCH=... savedefconfig` to detect unintended symbol churn, and build representative platform defconfigs. For `arch/arm/Kconfig`, also test `multi_v7_defconfig`, NOMMU/v7-M configurations, and selected errata combinations.

Source read size: 1751 lines, 59441 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/Makefile

## Purpose
This is the architecture Makefile for 32-bit ARM. It defines compiler, assembler, linker, endian, ABI, ISA, FPU, text-offset, machine-directory, image, install, and help targets consumed by the top-level kernel build.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `LDFLAGS_vmlinux`, `KBUILD_LDFLAGS_MODULE`, `GZFLAGS`, `KBUILD_CFLAGS`, `KBUILD_DEFCONFIG`, `MMUEXT`, `KBUILD_CPPFLAGS`, `CHECKFLAGS`, `KBUILD_LDFLAGS`, `arch-$(CONFIG_CPU_32v7M)`, `arch-$(CONFIG_CPU_32v7)`, `arch-$(CONFIG_CPU_32v6)`, `arch-$(CONFIG_CPU_32v6K)`, `arch-$(CONFIG_CPU_32v5)`, `arch-$(CONFIG_CPU_32v4T)`, `arch-$(CONFIG_CPU_32v4)`, `arch-$(CONFIG_CPU_32v3)`, `cpp-$(CONFIG_CPU_32v7M)`, `cpp-$(CONFIG_CPU_32v7)`, `cpp-$(CONFIG_CPU_32v6)`, `cpp-$(CONFIG_CPU_32v6K)`, `cpp-$(CONFIG_CPU_32v5)`, `cpp-$(CONFIG_CPU_32v4T)`, `cpp-$(CONFIG_CPU_32v4)`, `cpp-$(CONFIG_CPU_32v3)`, `tune-$(CONFIG_CPU_ARM7TDMI)`, `tune-$(CONFIG_CPU_ARM720T)`, `tune-$(CONFIG_CPU_ARM740T)`, and 96 more. Conditional gates include `CONFIG_CPU_ENDIAN_BE8`, `CONFIG_FRAME_POINTER`, `CONFIG_CC_IS_GCC`, `CONFIG_CPU_BIG_ENDIAN`, `CONFIG_CPU_32v6`, `CONFIG_AEABI`, `CONFIG_ARM_UNWIND`, `CONFIG_CC_IS_CLANG`, `CONFIG_CURRENT_POINTER_IN_TPIDRURO`, `CONFIG_THUMB2_KERNEL`, `CONFIG_ARCH_SA1100`, `CONFIG_XIP_KERNEL`, `CONFIG_STACKPROTECTOR_PER_TASK`, `CONFIG_CC_HAVE_STACKPROTECTOR_TLS`.

## Control Flow
The top-level build includes this file after Kconfig resolution. It accumulates KBUILD flags based on CPU, endian, ABI, Thumb, frame pointer, unwinder, Rust, and stack protector settings; maps enabled machines into `core-y`; exports `TEXT_OFFSET`, `GZFLAGS`, and `MMUEXT`; sets the default kernel image to `zImage` or `xipImage`; and forwards boot image targets into `arch/arm/boot`.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are flag combinations that break older toolchains, wrong `TEXT_OFFSET` for a platform, missing machine directory mappings, endian/linker flag mismatches, and stack protector offset extraction failures from generated asm offsets.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 332 lines, 11783 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/Makefile

## Purpose
This Makefile builds ARM boot images: raw `Image`, compressed `zImage`, XIP `xipImage`, U-Boot `uImage`, and BOOTP-wrapped `bootpImage`.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `OBJCOPYFLAGS`, `add_hex`, `ZRELADDR`, `PHYS_OFFSET`, `targets`, `cmd_deflate_xip_data`, `quiet_cmd_mkxip`, `cmd_mkxip`, `check_for_multiple_loadaddr`, `subdir-`. Conditional gates include `CONFIG_XIP_KERNEL`, `CONFIG_XIP_DEFLATED_DATA`.

## Control Flow
For non-XIP builds it objcopies `vmlinux` to `Image`, builds `compressed/vmlinux`, and objcopies that to `zImage`. For XIP builds it creates `xipImage`, optionally runs `deflate_xip_data.sh`, and rejects incompatible `Image`/`zImage` targets. `uImage` validates a single load address, while `bootpImage` delegates to the `bootp` subdirectory.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are inconsistent `PHYS_OFFSET`, `TEXT_OFFSET`, `ZRELADDR`, or `LOADADDR`, unsupported XIP target combinations, and BOOTP/uImage load addresses that do not match the bootloader.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 92 lines, 2412 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile

## Purpose
This Makefile links the legacy ARM BOOTP wrapper that combines a zImage with an initrd and ATAG parameter setup.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `add_hex`, `PARAMS_PHYS`, `initrd_offset-$(CONFIG_ARCH_FOOTBRIDGE)`, `initrd_offset-$(CONFIG_ARCH_SA1100)`, `initrd_offset-$(CONFIG_ARCH_RPC)`, `INITRD_OFFSET`, `INITRD_PHYS`, `PHONY`, `LDFLAGS_bootp`, `AFLAGS_initrd.o`, `targets`. Conditional gates include none.

## Control Flow
It derives `PARAMS_PHYS` and sometimes `INITRD_PHYS` from `PHYS_OFFSET`, validates `INITRD`, builds `init.o`, `kernel.o`, and `initrd.o`, and links them with `bootp.lds`. The resulting binary is later objcopied by the parent boot Makefile.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are missing `INITRD`, invalid `PARAMS_PHYS` or `INITRD_PHYS`, untracked `.incbin` inputs, and load addresses that put the initrd outside usable RAM.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 59 lines, 1823 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S

## Purpose
This BOOTP wrapper entry moves an embedded initrd to its linked physical destination, appends an `ATAG_INITRD2` record to the boot tag list, and then jumps to the embedded zImage.

## Important APIs, Types, and Functions
Assembly-visible symbols include `_start`, `taglist`, `move`, `data`. Included source files are none. Embedded binary inputs are none.

## Control Flow
`_start` computes its load address, copies the initrd in 32-byte chunks, creates a minimal `ATAG_CORE` if the parameter list is invalid, walks to the ATAG terminator, writes the initrd tag, and branches to `kernel_start`.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are invalid `params_phys`, overlapping initrd copy ranges, missing ATAG terminators, and bootloaders that pass only FDT data when this wrapper expects ATAG mutation.

## Test Signals
Build `bootpImage` with a known initrd and boot it on a legacy ATAG-capable ARM target; inspect the kernel log for initrd discovery and verify no memory overlap with zImage.

Source read size: 85 lines, 2477 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/init.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/initrd.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/initrd.S

## Purpose
This assembly wrapper exposes binary payload boundaries for the ARM boot build using `.incbin` data.

## Important APIs, Types, and Functions
Assembly-visible symbols include `initrd_start`, `initrd_end`. Included source files are none. Embedded binary inputs are `INITRD`.

## Control Flow
The assembler places the referenced binary into the output object and defines start/end symbols consumed by linker scripts or startup assembly.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are stale or missing binary inputs, missing dependencies for `.incbin` payloads, alignment mistakes, and linker script assumptions about symbol names.

## Test Signals
Run the corresponding boot image target and confirm the generated object rebuilds when the embedded binary changes; inspect symbols with `nm` or `objdump`.

Source read size: 7 lines, 149 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/initrd.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/kernel.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/kernel.S

## Purpose
This assembly wrapper exposes binary payload boundaries for the ARM boot build using `.incbin` data.

## Important APIs, Types, and Functions
Assembly-visible symbols include `kernel_start`, `kernel_end`. Included source files are none. Embedded binary inputs are `"arch/arm/boot/zImage"`.

## Control Flow
The assembler places the referenced binary into the output object and defines start/end symbols consumed by linker scripts or startup assembly.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are stale or missing binary inputs, missing dependencies for `.incbin` payloads, alignment mistakes, and linker script assumptions about symbol names.

## Test Signals
Run the corresponding boot image target and confirm the generated object rebuilds when the embedded binary changes; inspect symbols with `nm` or `objdump`.

Source read size: 7 lines, 147 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile

## Purpose
This Makefile builds the self-relocating ARM zImage decompressor and links it with compressed kernel payload data.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `OBJS`, `HEAD`, `AFLAGS_head.o`, `CFLAGS_string.o`, `ZTEXTADDR`, `ZBSSADDR`, `MALLOC_SIZE`, `CPPFLAGS_vmlinux.lds`, `compress-$(CONFIG_KERNEL_GZIP)`, `compress-$(CONFIG_KERNEL_LZO)`, `compress-$(CONFIG_KERNEL_LZMA)`, `compress-$(CONFIG_KERNEL_XZ)`, `compress-$(CONFIG_KERNEL_LZ4)`, `libfdt_objs`, `CFLAGS_REMOVE_atags_to_fdt.o`, `CFLAGS_atags_to_fdt.o`, `targets`, `KBUILD_CFLAGS`, `ccflags-y`, `ccflags-remove-$(CONFIG_FUNCTION_TRACER)`, `asflags-y`, `KBSS_SZ`, `LDFLAGS_vmlinux`, `check_for_bad_syms`, `bad_syms`, `check_for_multiple_zreladdr`, `efi-obj-$(CONFIG_EFI_STUB)`, `CFLAGS_font.o`. Conditional gates include `CONFIG_DEBUG_UNCOMPRESS`, `CONFIG_ARM_VIRT_EXT`, `CONFIG_ARCH_ACORN`, `CONFIG_ARCH_SA1100`, `CONFIG_CPU_XSCALE`, `CONFIG_PXA_SHARPSL_DETECT_MACH_ID`, `CONFIG_CPU_ENDIAN_BE32`, `CONFIG_CPU_CP15`, `CONFIG_ZBOOT_ROM`, `CONFIG_ARM_ATAG_DTB_COMPAT`, `CONFIG_USE_OF`, `CONFIG_CPU_ENDIAN_BE8`.

## Control Flow
It selects head and helper objects based on debug, virtualization, platform, endian, ATAG/FDT, and compression configuration; sets PIC and freestanding C flags; generates `piggy_data` with the chosen compressor; links decompressor `vmlinux` with `vmlinux.lds`; validates `ZRELADDR`; and rejects local/private BSS symbols that the runtime GOT relocation code cannot safely fix up.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are non-PIC references, bad BSS/GOT relocation, unsupported compressor object selection, incorrect `_kernel_bss_size`, multiple `ZRELADDR` values without `AUTO_ZRELADDR`, and missing libfdt or helper symbols in the constrained decompressor environment.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 160 lines, 4673 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ashldi3.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ashldi3.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are `"../../lib/ashldi3.S"`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 3 lines, 98 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ashldi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c

## Purpose
This decompressor helper converts legacy ARM ATAG boot parameters into properties inside an appended or supplied flattened device tree before the real kernel starts. It handles bootargs, memory banks, initrd location, and serial number propagation.

## Important APIs, Types, and Functions
Functions and exported helpers include `node_offset`, `setprop`, `setprop_string`, `setprop_cell`, `get_cell_size`, `merge_fdt_bootargs`, `hex_str`, `atags_to_fdt`, `for_each_tag`. Local constants include `do_extend_cmdline`, `NR_BANKS`. Includes are `<linux/libfdt_env.h>`, `<asm/setup.h>`, `<libfdt.h>`, `"misc.h"`.

## Control Flow
`atags_to_fdt()` validates alignment and ATAG_CORE, expands the FDT with `fdt_open_into`, walks each tag, updates `/chosen` bootargs, records `linux,initrd-start/end`, serializes up to 16 memory banks using the DT root `#size-cells`, and repacks the FDT. If the input already points to a DTB it returns success without conversion; bad ATAG locations return `1` so the assembly caller can retry the conventional RAM+0x100 address.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are insufficient temporary FDT space, command line truncation, incorrect cell-size handling for 64-bit memory sizes, silently skipping more than 16 memory banks, and conflicting DT/ATAG bootargs where append versus replace policy changes command-line precedence.

## Test Signals
Boot with `CONFIG_ARM_ATAG_DTB_COMPAT` using ATAG-only, DTB-only, and mixed ATAG+appended-DTB flows. Validate `/chosen/bootargs`, initrd properties, `serial-number`, and `/memory/reg` in the resulting FDT and include command-line extension versus replacement configurations.

Source read size: 218 lines, 5572 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/atags_to_fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S

## Purpose
This startup fragment switches capable ARM CPUs into big-endian mode for BE32 decompressor configurations.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are none. Embedded binary inputs are none.

## Control Flow
It reads CP15 control register c1, sets the big-endian bit, and writes the control register back in the `.start` section before the rest of decompressor startup proceeds.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are executing on a CPU/configuration where CP15 endian switching is unavailable or already controlled by hardware design.

## Test Signals
Build BE32/CP15 configurations and boot under an emulator or board that supports the mode; verify early decompressor and kernel endianness.

Source read size: 14 lines, 329 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/bswapsdi2.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/bswapsdi2.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are `"../../lib/bswapsdi2.S"`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 3 lines, 110 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/bswapsdi2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/debug.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/debug.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include `putc`, `semi_writec_buf`. Included source files are `<linux/linkage.h>`, `<asm/assembler.h>`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 48 lines, 801 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/debug.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c

## Purpose
This file selects and wraps the configured kernel decompressor implementation for the ARM zImage decompressor.

## Important APIs, Types, and Functions
Functions and exported helpers include `do_decompress`. Local constants include `_LINUX_STRING_H_`, `STATIC`, `STATIC_RW_DATA`, `Assert`, `Trace`, `Tracev`, `Tracevv`, `Tracec`, `Tracecv`, `memmove`, `memcpy`. Includes are `<linux/compiler.h>`, `<linux/types.h>`, `<linux/stddef.h>`, `<linux/linkage.h>`, `<asm/string.h>`, `"misc.h"`, `"../../../../lib/decompress_inflate.c"`, `"../../../../lib/decompress_unlzo.c"`, `"../../../../lib/decompress_unlzma.c"`, `"../../../../lib/decompress_unxz.c"`, `"../../../../lib/decompress_unlz4.c"`.

## Control Flow
The preprocessor includes exactly the decompressor backend selected by `CONFIG_KERNEL_GZIP`, `LZO`, `LZMA`, `XZ`, or `LZ4`, defines standalone diagnostic/string hooks needed by those sources, and `do_decompress()` calls the common `__decompress()` entry on `input_data` and the output buffer supplied by `misc.c`.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are missing string helpers in the freestanding decompressor environment, KASAN/fortify macro conflicts, multiple or no compressor configurations, and backend memory requirements exceeding the 64 KiB malloc window.

## Test Signals
Build and boot zImages for each supported compressor. Corrupt `piggy_data` for a negative test and confirm `error()` halts cleanly. Use `V=1` to verify only the intended decompressor backend is included.

Source read size: 66 lines, 1817 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S

## Purpose
This assembly include emits the ARM zImage EFI/PE-COFF header metadata used when `CONFIG_EFI_STUB` makes the compressed image bootable by EFI firmware.

## Important APIs, Types, and Functions
Assembly-visible symbols include `pe_header`, `coff_header`, `optional_header`, `extra_header_fields`, `section_table`, `__efi_start`. Included source files are `<linux/pe.h>`, `<linux/sizes.h>`. Embedded binary inputs are none.

## Control Flow
It contributes header fields and size calculations to `head.S`; firmware reads the PE/COFF layout before jumping to the decompressor entry.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are incorrect header sizes, section alignment, or entry metadata that make EFI firmware reject or misload the zImage.

## Test Signals
Build with `CONFIG_EFI_STUB`, inspect the PE header with EFI-aware tools, and boot through UEFI on ARM hardware or QEMU.

Source read size: 136 lines, 4236 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/efi-header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt.c

## Purpose
This compressed-boot C/header file provides small helper declarations or platform-specific setup used before the normal ARM kernel runtime exists.

## Important APIs, Types, and Functions
Functions and exported helpers include none. Local constants include none. Includes are `"../../../../lib/fdt.c"`.

## Control Flow
The file is compiled into the decompressor or included by decompressor sources and executes only during zImage startup, before MMU-managed kernel code and normal drivers are available.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are using unavailable kernel facilities, touching platform registers too early, and changing ABI-visible helper declarations used by assembly startup code.

## Test Signals
Build the affected compressed boot configuration and boot it under a board or emulator that exercises the helper.

Source read size: 2 lines, 74 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c

## Purpose
This decompressor helper validates or corrects the physical memory base computed by `AUTO_ZRELADDR` using the supplied FDT memory nodes and optional crash-kernel usable-memory range.

## Important APIs, Types, and Functions
Functions and exported helpers include `get_cells`, `get_val`, `compatibility`. Local constants include none. Includes are `<linux/kernel.h>`, `<linux/libfdt.h>`, `<linux/sizes.h>`, `"misc.h"`.

## Control Flow
`fdt_check_mem_start()` rejects missing/non-FDT input, reads root address/size cell counts, optionally clips memory ranges by `/chosen/linux,usable-memory-range`, walks memory nodes and `linux,usable-memory` or `reg` properties, returns the original masked PC-derived base if it is valid, or otherwise returns the lowest usable base rounded up to 2 MiB.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are malformed cell counts, memory above the 32-bit address space, incorrect clipping for crash kernels, failure to find a memory node, and choosing a base that violates ARM phys/virt patching alignment assumptions.

## Test Signals
Exercise boot with FDT memory starts that are and are not 128 MiB aligned, with multiple memory banks, with `linux,usable-memory-range`, and with invalid DTBs. Confirm the chosen start matches the kernel log and does not overlap reserved crash regions.

Source read size: 168 lines, 4426 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_check_mem_start.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_ro.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_ro.c

## Purpose
This compressed-boot C/header file provides small helper declarations or platform-specific setup used before the normal ARM kernel runtime exists.

## Important APIs, Types, and Functions
Functions and exported helpers include none. Local constants include none. Includes are `"../../../../lib/fdt_ro.c"`.

## Control Flow
The file is compiled into the decompressor or included by decompressor sources and executes only during zImage startup, before MMU-managed kernel code and normal drivers are available.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are using unavailable kernel facilities, touching platform registers too early, and changing ABI-visible helper declarations used by assembly startup code.

## Test Signals
Build the affected compressed boot configuration and boot it under a board or emulator that exercises the helper.

Source read size: 2 lines, 77 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_ro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_rw.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_rw.c

## Purpose
This compressed-boot C/header file provides small helper declarations or platform-specific setup used before the normal ARM kernel runtime exists.

## Important APIs, Types, and Functions
Functions and exported helpers include none. Local constants include none. Includes are `"../../../../lib/fdt_rw.c"`.

## Control Flow
The file is compiled into the decompressor or included by decompressor sources and executes only during zImage startup, before MMU-managed kernel code and normal drivers are available.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are using unavailable kernel facilities, touching platform registers too early, and changing ABI-visible helper declarations used by assembly startup code.

## Test Signals
Build the affected compressed boot configuration and boot it under a board or emulator that exercises the helper.

Source read size: 2 lines, 77 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_wip.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_wip.c

## Purpose
This compressed-boot C/header file provides small helper declarations or platform-specific setup used before the normal ARM kernel runtime exists.

## Important APIs, Types, and Functions
Functions and exported helpers include none. Local constants include none. Includes are `"../../../../lib/fdt_wip.c"`.

## Control Flow
The file is compiled into the decompressor or included by decompressor sources and executes only during zImage startup, before MMU-managed kernel code and normal drivers are available.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are using unavailable kernel facilities, touching platform registers too early, and changing ABI-visible helper declarations used by assembly startup code.

## Test Signals
Build the affected compressed boot configuration and boot it under a board or emulator that exercises the helper.

Source read size: 2 lines, 78 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/fdt_wip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/font.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/font.c

## Purpose
This compressed-boot C/header file provides small helper declarations or platform-specific setup used before the normal ARM kernel runtime exists.

## Important APIs, Types, and Functions
Functions and exported helpers include none. Local constants include none. Includes are `"../../../../lib/fonts/font_acorn_8x8.c"`.

## Control Flow
The file is compiled into the decompressor or included by decompressor sources and executes only during zImage startup, before MMU-managed kernel code and normal drivers are available.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are using unavailable kernel facilities, touching platform registers too early, and changing ABI-visible helper declarations used by assembly startup code.

## Test Signals
Build the affected compressed boot configuration and boot it under a board or emulator that exercises the helper.

Source read size: 2 lines, 91 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/font.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sa1100.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sa1100.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include `__SA1100_start`. Included source files are `<linux/linkage.h>`, `<asm/mach-types.h>`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 45 lines, 1167 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sa1100.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sharpsl.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sharpsl.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include `__SharpSL_start`, `get_flash_ids`. Included source files are `<linux/linkage.h>`, `<asm/mach-types.h>`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 151 lines, 3603 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-sharpsl.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-xscale.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-xscale.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include `__XScale_start`. Included source files are `<linux/linkage.h>`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 35 lines, 916 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head-xscale.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S

## Purpose
This is the ARM zImage decompressor entry and relocation assembly. It handles legacy boot headers, ARM/Thumb state, optional EFI header data, AUTO_ZRELADDR memory-base calculation, appended DTB and ATAG-to-FDT handling, self-relocation, GOT/BSS fixups, cache/MMU/MPU setup and teardown, decompressor invocation, HYP-mode handoff, and final branch into the decompressed kernel.

## Important APIs, Types, and Functions
Assembly-visible symbols include `efi_enter_kernel`, `start`, `not_angel`, `restart`, `dtb_check_done`, `wont_overwrite`, `not_relocated`, `LC0`, `LC1`, `params`, `cache_on`, `__armv4_mpu_cache_on`, `__armv3_mpu_cache_on`, `__setup_mmu`, `__armv6_mmu_cache_on`, `__arm926ejs_mmu_cache_on`, `__armv4_mmu_cache_on`, `__armv7_mmu_cache_on`, `__fa526_cache_on`, `__common_mmu_cache_on`, `call_cache_fn`, `proc_types`, `cache_off`, `__armv4_mpu_cache_off`, and 24 more. Included source files are `<linux/linkage.h>`, `<asm/assembler.h>`, `<asm/v7m.h>`, `"efi-header.S"`. Embedded binary inputs are none.

## Control Flow
Execution enters at `start`, preserves boot registers, normalizes CPU mode, computes the final kernel load address, optionally validates it through FDT memory data, decides whether a temporary page table/cache setup is safe, relocates the decompressor if it would overlap the inflated kernel, fixes GOT and BSS pointers, clears BSS, calls `decompress_kernel`, flushes caches, disables cache/MMU state, and then jumps to the kernel entry or HYP re-entry path. Processor tables near the end dispatch CPU-specific cache on/off/flush routines.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are severe: wrong relocation bounds can overwrite the decompressor or inflated kernel, bad GOT/BSS fixups break C code, incorrect cache maintenance can execute stale instructions, appended DTB growth can collide with BSS, and boot-mode/HYP handling mistakes can strand the CPU before the kernel entry point.

## Test Signals
Boot zImage on ARMv4/v5/v6/v7, Thumb2, BE8, AUTO_ZRELADDR, appended-DTB, ATAG compatibility, EFI stub, and HYP-mode configurations. Use `DEBUG_UNCOMPRESS` to inspect relocation and DTB diagnostics, and verify cache flush/off paths on real hardware or accurate emulators.

Source read size: 1531 lines, 39017 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/hyp-stub.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/hyp-stub.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are `"../../kernel/hyp-stub.S"`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 2 lines, 79 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/hyp-stub.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/lib1funcs.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/lib1funcs.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are `"../../lib/lib1funcs.S"`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 3 lines, 104 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/lib1funcs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S

## Purpose
This Acorn-specific decompressor helper writes characters to the early low-level display path and carries the character conversion table used by that path.

## Important APIs, Types, and Functions
Assembly-visible symbols include `ll_write_char`, `con_charconvtable`, `LC0`, `Lrow4bpplp`, `Lrow8bpplp`, `Lrow1bpp`. Included source files are `<linux/linkage.h>`, `<asm/assembler.h>`. Embedded binary inputs are none.

## Control Flow
`ll_write_char` converts or emits character data using the table symbols before normal console drivers are available.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are display memory assumptions, conversion table mismatches, and debug output faults before the kernel console is initialized.

## Test Signals
Build an Acorn/RPC-style compressed boot with debug output and confirm early characters appear correctly.

Source read size: 131 lines, 2722 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/ll_char_wr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h

## Purpose
This header provides declarations or platform-specific inline helpers for the ARM compressed boot environment, where normal kernel headers and drivers are not available.

## Important APIs, Types, and Functions
Declared or inline helpers include `Copyright`, `__raw_writeb`, `__raw_writel`, `ep93xx_ethernet_reset`, `ts72xx_watchdog_disable`, `ep93xx_decomp_setup`. Constants and guards include `PHYS_ETH_SELF_CTL`, `ETH_SELF_CTL_RESET`, `TS72XX_WDT_CONTROL_PHYS_BASE`, `TS72XX_WDT_FEED_PHYS_BASE`, `TS72XX_WDT_FEED_VAL`.

## Control Flow
The header is included by compressed boot C code. Inline helpers execute only if the including decompressor path calls them, typically before cache/MMU setup and before normal platform drivers exist.

## State and Persistence Behavior
State is limited to early MMIO side effects, decompressor globals, or declarations used by linked decompressor objects. Nothing is stored persistently, but early register writes can affect subsequent boot hardware state.

## Dependencies and Integration Points
Integration points include `misc.c`, `decompress.c`, platform-specific decompressor setup, low-level MMIO addresses, and the compressed linker/build rules.

## Risks
Risks are stale physical addresses, unavailable MMIO before the decompressor relocates, declaration mismatches across C/assembly boundaries, and hidden dependencies on bootloader-initialized hardware.

## Test Signals
Build the compressed boot configuration that includes this header and boot a target that exercises the helper. Inspect early boot output and hardware side effects such as watchdog disable or peripheral reset.

Source read size: 75 lines, 2004 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c

## Purpose
This file provides the small C runtime for the ARM zImage decompressor: console output, fatal error handling, global allocation bounds, machine type capture, optional EP93xx setup, and the call into `do_decompress()`.

## Important APIs, Types, and Functions
Functions and exported helpers include `icedcc_putc`, `putstr`, `error`, `__div0`, `decompress_kernel`, `__fortify_panic`. Local constants include `putc`, `arch_error`. Includes are `<linux/compiler.h>`, `<linux/types.h>`, `<linux/linkage.h>`, `"misc.h"`, `"misc-ep93xx.h"`.

## Control Flow
`decompress_kernel()` receives output address, malloc range, and architecture id from `head.S`; initializes `output_data`, `free_mem_ptr`, `free_mem_end_ptr`, and `__machine_arch_type`; runs platform decompressor setup; prints progress; calls `do_decompress()`; and either halts through `error()` or announces handoff to the kernel. Debug ICEDCC variants provide `putc()` when configured.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are printing through an uninitialized debug transport, malloc bounds too small for the decompressor, platform setup touching wrong early registers, division-by-zero or fortify panic paths looping before diagnostics are visible, and non-const initialized data breaking XIP assumptions.

## Test Signals
Boot with and without `DEBUG_UNCOMPRESS`, with EP93xx setup enabled, and with each compressor. Confirm the progress banner, successful handoff, and that bad compressed input reaches the halt path.

Source read size: 160 lines, 3066 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.h

## Purpose
This header provides declarations or platform-specific inline helpers for the ARM compressed boot environment, where normal kernel headers and drivers are not available.

## Important APIs, Types, and Functions
Declared or inline helpers include none. Constants and guards include `MISC_H`.

## Control Flow
The header is included by compressed boot C code. Inline helpers execute only if the including decompressor path calls them, typically before cache/MMU setup and before normal platform drivers exist.

## State and Persistence Behavior
State is limited to early MMIO side effects, decompressor globals, or declarations used by linked decompressor objects. Nothing is stored persistently, but early register writes can affect subsequent boot hardware state.

## Dependencies and Integration Points
Integration points include `misc.c`, `decompress.c`, platform-specific decompressor setup, low-level MMIO addresses, and the compressed linker/build rules.

## Risks
Risks are stale physical addresses, unavailable MMIO before the decompressor relocates, declaration mismatches across C/assembly boundaries, and hidden dependencies on bootloader-initialized hardware.

## Test Signals
Build the compressed boot configuration that includes this header and boot a target that exercises the helper. Inspect early boot output and hardware side effects such as watchdog disable or peripheral reset.

Source read size: 21 lines, 654 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/piggy.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/piggy.S

## Purpose
This assembly wrapper exposes binary payload boundaries for the ARM boot build using `.incbin` data.

## Important APIs, Types, and Functions
Assembly-visible symbols include `input_data`, `input_data_end`. Included source files are none. Embedded binary inputs are `"arch/arm/boot/compressed/piggy_data"`.

## Control Flow
The assembler places the referenced binary into the output object and defines start/end symbols consumed by linker scripts or startup assembly.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are stale or missing binary inputs, missing dependencies for `.incbin` payloads, alignment mistakes, and linker script assumptions about symbol names.

## Test Signals
Run the corresponding boot image target and confirm the generated object rebuilds when the embedded binary changes; inspect symbols with `nm` or `objdump`.

Source read size: 7 lines, 182 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/piggy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c

## Purpose
This file implements minimal freestanding string and memory routines for the compressed ARM boot environment, avoiding fortified libc/kernel string dependencies before the full kernel is running.

## Important APIs, Types, and Functions
Functions and exported helpers include `strlen`, `strnlen`, `memcmp`, `strcmp`. Local constants include `__NO_FORTIFY`. Includes are `<linux/string.h>`.

## Control Flow
`memcpy`, `memmove`, `memcmp`, `strcmp`, `memchr`, `strchr`, `strrchr`, and `memset` operate directly on byte pointers. `memmove` chooses forward or backward copying for overlap. Alias symbols provide `__memcpy`, `__memmove`, and `__memset` names expected by compiler-generated calls.

## State and Persistence Behavior
State is transient decompressor state in registers, BSS, the temporary malloc area, and possibly the in-memory FDT. It persists only until the decompressed kernel takes control, but it directly determines the kernel image bytes, boot arguments, initrd metadata, memory base, and early diagnostics seen by the real kernel.

## Dependencies and Integration Points
Dependencies include `head.S`, `misc.h`, the compressed linker script, libfdt sources where enabled, configured decompressor backends, generated `piggy_data`, debug UART/ICEDCC hooks, and bootloader-provided ATAG/FDT/register conventions.

## Risks
Risks are overlap mistakes in `memmove`, compiler replacement with unavailable builtins, performance regressions in the decompressor, and missing helper variants required by a newly included decompressor backend.

## Test Signals
Build compressed images with each compiler and compressor, then run unit-style checks in a host harness if extracted. Boot tests should include XZ, because that path explicitly protects `memmove`/`memcpy` macro behavior.

Source read size: 162 lines, 2971 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/vmlinux.lds.S

## Purpose
This assembly file is a thin compressed-boot wrapper around shared ARM library or platform startup code.

## Important APIs, Types, and Functions
Assembly-visible symbols include `_start`. Included source files are `<asm/vmlinux.lds.h>`. Embedded binary inputs are none.

## Control Flow
It is assembled into the decompressor when selected by the compressed Makefile and either includes shared implementation text or provides a small CPU/platform-specific startup action.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are include path drift, missing helper symbols expected by compiler-generated calls, and pulling code into the constrained decompressor environment that is not position independent.

## Test Signals
Build the compressed image configuration that selects this object and inspect the decompressor link for unresolved symbols.

Source read size: 144 lines, 3426 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh -->
# sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh

## Purpose
This script post-processes an ARM XIP kernel image by replacing the file's trailing `.data` region with a gzip-compressed copy. It is used by the boot Makefile when both `CONFIG_XIP_KERNEL` and `CONFIG_XIP_DEFLATED_DATA` are enabled.

## Important APIs, Types, and Functions
Shell variables include `VMLINUX`, `XIPIMAGE`, `DD`, `__data_loc`, `_edata_loc`, `base_offset`, `data_start`, `data_end`, `file_end` and helper functions include `sym_val`. It relies on `$NM`, `$KGZIP`, `$CONFIG_SHELL`, `$srctree/scripts/file-size.sh`, and `dd status=none` with byte count/skip flags.

## Control Flow
The script enables `set -e`, optionally enables shell tracing for verbose builds, extracts `__data_loc`, `_edata_loc`, and `_xiprom` symbol values from `vmlinux`, converts them to file offsets, verifies `_edata_loc` matches the end of `xipImage`, installs a cleanup trap, copies bytes before `.data` into a temporary image, pipes the `.data` suffix through gzip, appends it, and atomically replaces the image.

## State and Persistence Behavior
The persistent artifact is the modified `xipImage`. Temporary state is `xipImage.tmp`, removed on signal-trap failure. The script intentionally mutates the image in place after validating symbol/file-size consistency.

## Dependencies and Integration Points
Integration is with `arch/arm/boot/Makefile` XIP image rules, the linked `vmlinux` symbol table, the generated raw `xipImage`, shell tools, `KGZIP`, and kernel boot code that knows how to inflate the compressed XIP data section.

## Risks
Risks include missing symbols, `NM` output format changes, a data section that is not the final file region, `dd` implementations without byte-count flags, interrupted writes before `mv`, and boot failures if the decompressor and image layout disagree about compressed `.data` placement.

## Test Signals
Build `make ARCH=arm xipImage` with XIP deflated data enabled, run with `KBUILD_VERBOSE=1`, verify the image shrinks/changes after `.data`, and boot the XIP image on a supported target. Negative tests should alter symbol expectations or truncate the image and confirm the script exits before replacement.

Source read size: 62 lines, 1663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `dts`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `subdir-y`. Conditional gates include none. Subdirectory traversal includes `actions`, `airoha`, `allwinner`, `alphascale`, `amazon`, `amlogic`, `arm`, `aspeed`, `axis`, `broadcom`, `calxeda`, `cirrus`, `cnxt`, `gemini`, `hisilicon`, `hpe`, `intel`, `marvell`, `mediatek`, `microchip`, `moxa`, `nspire`, `nuvoton`, `nvidia`, and 16 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 41 lines, 803 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/actions/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/actions/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `actions`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_ACTIONS)`. Conditional gates include `CONFIG_ARCH_ACTIONS`. It lists 5 DTB targets, including `owl-s500-cubieboard6.dtb`, `owl-s500-guitar-bb-rev-b.dtb`, `owl-s500-labrador-base-m.dtb`, `owl-s500-roseapplepi.dtb`, `owl-s500-sparky.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 7 lines, 208 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/actions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/airoha/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/airoha/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `airoha`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_AIROHA)`. Conditional gates include `CONFIG_ARCH_AIROHA`. It lists 1 DTB targets, including `en7523-evb.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 3 lines, 82 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/airoha/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/allwinner/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/allwinner/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `allwinner`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_MACH_SUN4I)`, `dtb-$(CONFIG_MACH_SUN5I)`, `dtb-$(CONFIG_MACH_SUN6I)`, `dtb-$(CONFIG_MACH_SUN7I)`, `DTC_FLAGS_sun8i-h2-plus-orangepi-zero`, `DTC_FLAGS_sun8i-h3-orangepi-lite`, `DTC_FLAGS_sun8i-h3-bananapi-m2-plus`, `DTC_FLAGS_sun8i-h3-nanopi-m1-plus`, `DTC_FLAGS_sun8i-h3-nanopi-m1`, `DTC_FLAGS_sun8i-h3-nanopi-duo2`, `DTC_FLAGS_sun8i-h3-orangepi-plus2e`, `DTC_FLAGS_sun8i-h3-orangepi-one`, `DTC_FLAGS_sun8i-h3-orangepi-plus`, `DTC_FLAGS_sun8i-h3-orangepi-2`, `DTC_FLAGS_sun8i-h3-orangepi-zero-plus2`, `DTC_FLAGS_sun8i-h3-nanopi-neo-air`, `DTC_FLAGS_sun8i-h3-zeropi`, `DTC_FLAGS_sun8i-h3-nanopi-neo`, `DTC_FLAGS_sun8i-h3-nanopi-r1`, `DTC_FLAGS_sun8i-h3-orangepi-pc`, `DTC_FLAGS_sun8i-h3-bananapi-m2-plus-v1.2`, `DTC_FLAGS_sun8i-h3-orangepi-pc-plus`, `DTC_FLAGS_sun8i-t113s-netcube-nagami-basic-carrier`, `DTC_FLAGS_sun8i-v3s-netcube-kumquat`, `dtb-$(CONFIG_MACH_SUN8I)`, `sun8i-h2-plus-orangepi-zero-interface-board-dtbs`, `sun8i-h3-orangepi-zero-plus2-interface-board-dtbs`, `dtb-$(CONFIG_MACH_SUN9I)`, and 1 more. Conditional gates include `CONFIG_MACH_SUN4I`, `CONFIG_MACH_SUN5I`, `CONFIG_MACH_SUN6I`, `CONFIG_MACH_SUN7I`, `CONFIG_MACH_SUN8I`, `CONFIG_MACH_SUN9I`, `CONFIG_MACH_SUNIV`. It lists 159 DTB targets, including `sun4i-a10-a1000.dtb`, `sun4i-a10-ba10-tvbox.dtb`, `sun4i-a10-chuwi-v7-cw0825.dtb`, `sun4i-a10-cubieboard.dtb`, `sun4i-a10-dserve-dsrv9703c.dtb`, `sun4i-a10-gemei-g9.dtb`, `sun4i-a10-hackberry.dtb`, `sun4i-a10-hyundai-a7hd.dtb`, `sun4i-a10-inet1.dtb`, `sun4i-a10-inet97fv2.dtb`, `sun4i-a10-inet9f-rev03.dtb`, `sun4i-a10-itead-iteaduino-plus.dtb`, `sun4i-a10-jesurun-q5.dtb`, `sun4i-a10-marsboard.dtb`, `sun4i-a10-mini-xplus.dtb`, `sun4i-a10-mk802.dtb`, `sun4i-a10-mk802ii.dtb`, `sun4i-a10-olinuxino-lime.dtb`, `sun4i-a10-pcduino.dtb`, `sun4i-a10-pcduino2.dtb`, `sun4i-a10-pov-protab2-ips9.dtb`, `sun4i-a10-topwise-a721.dtb`, `sun5i-a10s-auxtek-t003.dtb`, `sun5i-a10s-auxtek-t004.dtb`, and 135 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 283 lines, 8946 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/alphascale/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/alphascale/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `alphascale`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_MACH_ASM9260)`. Conditional gates include `CONFIG_MACH_ASM9260`. It lists 1 DTB targets, including `alphascale-asm9260-devkit.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 161 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/alphascale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/amazon/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/amazon/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `amazon`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_ALPINE)`. Conditional gates include `CONFIG_ARCH_ALPINE`. It lists 1 DTB targets, including `alpine-db.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 127 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/amazon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/amlogic/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `amlogic`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_MACH_MESON8)`. Conditional gates include `CONFIG_MACH_MESON8`. It lists 6 DTB targets, including `meson8-minix-neo-x8.dtb`, `meson8-fernsehfee3.dtb`, `meson8b-ec100.dtb`, `meson8b-mxq.dtb`, `meson8b-odroidc1.dtb`, `meson8m2-mxiii-plus.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 8 lines, 208 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `arm`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_INTEGRATOR)`, `dtb-$(CONFIG_ARCH_MPS2)`, `dtb-$(CONFIG_ARCH_REALVIEW)`, `dtb-$(CONFIG_ARCH_VERSATILE)`, `dtb-$(CONFIG_ARCH_VEXPRESS)`. Conditional gates include `CONFIG_ARCH_INTEGRATOR`, `CONFIG_ARCH_MPS2`, `CONFIG_ARCH_REALVIEW`, `CONFIG_ARCH_VERSATILE`, `CONFIG_ARCH_VEXPRESS`. It lists 24 DTB targets, including `integratorap.dtb`, `integratorap-im-pd1.dtb`, `integratorcp.dtb`, `mps2-an385.dtb`, `mps2-an399.dtb`, `arm-realview-pb1176.dtb`, `arm-realview-pb11mp.dtb`, `arm-realview-eb.dtb`, `arm-realview-eb-bbrevd.dtb`, `arm-realview-eb-11mp.dtb`, `arm-realview-eb-11mp-bbrevd.dtb`, `arm-realview-eb-11mp-ctrevb.dtb`, `arm-realview-eb-11mp-bbrevd-ctrevb.dtb`, `arm-realview-eb-a9mp.dtb`, `arm-realview-eb-a9mp-bbrevd.dtb`, `arm-realview-pba8.dtb`, `arm-realview-pbx-a9.dtb`, `versatile-ab.dtb`, `versatile-ab-ib2.dtb`, `versatile-pb.dtb`, `vexpress-v2p-ca5s.dtb`, `vexpress-v2p-ca9.dtb`, `vexpress-v2p-ca15-tc1.dtb`, `vexpress-v2p-ca15_a7.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 30 lines, 824 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/aspeed/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `aspeed`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_ASPEED)`. Conditional gates include `CONFIG_ARCH_ASPEED`. It lists 85 DTB targets, including `aspeed-ast2500-evb.dtb`, `aspeed-ast2600-evb-a1.dtb`, `aspeed-ast2600-evb.dtb`, `aspeed-bmc-amd-daytonax.dtb`, `aspeed-bmc-amd-ethanolx.dtb`, `aspeed-bmc-ampere-mtjade.dtb`, `aspeed-bmc-ampere-mtjefferson.dtb`, `aspeed-bmc-ampere-mtmitchell.dtb`, `aspeed-bmc-arm-stardragon4800-rep2.dtb`, `aspeed-bmc-asrock-altrad8.dtb`, `aspeed-bmc-asrock-e3c246d4i.dtb`, `aspeed-bmc-asrock-e3c256d4i.dtb`, `aspeed-bmc-asrock-paul-ipmi-card.dtb`, `aspeed-bmc-asrock-romed8hm3.dtb`, `aspeed-bmc-asrock-spc621d8hm3.dtb`, `aspeed-bmc-asrock-x570d4u.dtb`, `aspeed-bmc-asus-kommando-ipmi-card.dtb`, `aspeed-bmc-asus-x4tf.dtb`, `aspeed-bmc-bytedance-g220a.dtb`, `aspeed-bmc-delta-ahe50dc.dtb`, `aspeed-bmc-facebook-anacapa.dtb`, `aspeed-bmc-facebook-bletchley.dtb`, `aspeed-bmc-facebook-catalina.dtb`, `aspeed-bmc-facebook-clemente.dtb`, and 61 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 87 lines, 2907 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/aspeed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/axis/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/axis/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `axis`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_MACH_ARTPEC6)`. Conditional gates include `CONFIG_MACH_ARTPEC6`. It lists 1 DTB targets, including `artpec6-devboard.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 143 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/axis/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `broadcom`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `DTC_FLAGS_bcm2835-rpi-b`, `DTC_FLAGS_bcm2835-rpi-a`, `DTC_FLAGS_bcm2835-rpi-b-rev2`, `DTC_FLAGS_bcm2835-rpi-b-plus`, `DTC_FLAGS_bcm2835-rpi-a-plus`, `DTC_FLAGS_bcm2835-rpi-cm1-io1`, `DTC_FLAGS_bcm2836-rpi-2-b`, `DTC_FLAGS_bcm2837-rpi-2-b`, `DTC_FLAGS_bcm2837-rpi-3-a-plus`, `DTC_FLAGS_bcm2837-rpi-3-b`, `DTC_FLAGS_bcm2837-rpi-3-b-plus`, `DTC_FLAGS_bcm2837-rpi-cm3-io3`, `DTC_FLAGS_bcm2837-rpi-zero-2-w`, `DTC_FLAGS_bcm2711-rpi-400`, `DTC_FLAGS_bcm2711-rpi-4-b`, `DTC_FLAGS_bcm2711-rpi-cm4-io`, `DTC_FLAGS_bcm2835-rpi-zero`, `DTC_FLAGS_bcm2835-rpi-zero-w`, `dtb-$(CONFIG_ARCH_BCM2835)`, `dtb-$(CONFIG_ARCH_BCMBCA)`, `dtb-$(CONFIG_ARCH_BCM_5301X)`, `dtb-$(CONFIG_ARCH_BCM_53573)`, `dtb-$(CONFIG_ARCH_BCM_CYGNUS)`, `dtb-$(CONFIG_ARCH_BCM_HR2)`, `dtb-$(CONFIG_ARCH_BCM_MOBILE)`, `dtb-$(CONFIG_ARCH_BCM_NSP)`, `dtb-$(CONFIG_ARCH_BRCMSTB)`. Conditional gates include `CONFIG_ARCH_BCM2835`, `CONFIG_ARCH_BCMBCA`, `CONFIG_ARCH_BCM_5301X`, `CONFIG_ARCH_BCM_53573`, `CONFIG_ARCH_BCM_CYGNUS`, `CONFIG_ARCH_BCM_HR2`, `CONFIG_ARCH_BCM_MOBILE`, `CONFIG_ARCH_BCM_NSP`, `CONFIG_ARCH_BRCMSTB`. It lists 103 DTB targets, including `bcm2835-rpi-b.dtb`, `bcm2835-rpi-a.dtb`, `bcm2835-rpi-b-rev2.dtb`, `bcm2835-rpi-b-plus.dtb`, `bcm2835-rpi-a-plus.dtb`, `bcm2835-rpi-cm1-io1.dtb`, `bcm2836-rpi-2-b.dtb`, `bcm2837-rpi-2-b.dtb`, `bcm2837-rpi-3-a-plus.dtb`, `bcm2837-rpi-3-b.dtb`, `bcm2837-rpi-3-b-plus.dtb`, `bcm2837-rpi-cm3-io3.dtb`, `bcm2837-rpi-zero-2-w.dtb`, `bcm2711-rpi-400.dtb`, `bcm2711-rpi-4-b.dtb`, `bcm2711-rpi-cm4-io.dtb`, `bcm2835-rpi-zero.dtb`, `bcm2835-rpi-zero-w.dtb`, `bcm6846-genexis-xg6846b.dtb`, `bcm947622.dtb`, `bcm963138.dtb`, `bcm963138dvt.dtb`, `bcm963148.dtb`, `bcm963178.dtb`, and 79 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 132 lines, 3694 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/calxeda/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/calxeda/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `calxeda`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_HIGHBANK)`. Conditional gates include `CONFIG_ARCH_HIGHBANK`. It lists 2 DTB targets, including `highbank.dtb`, `ecx-2000.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 7 lines, 161 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/calxeda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/cirrus/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `cirrus`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_CLPS711X)`, `dtb-$(CONFIG_ARCH_EP93XX)`. Conditional gates include `CONFIG_ARCH_CLPS711X`, `CONFIG_ARCH_EP93XX`. It lists 4 DTB targets, including `ep7211-edb7211.dtb`, `ep93xx-edb9302.dtb`, `ep93xx-bk3.dtb`, `ep93xx-ts7250.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 9 lines, 231 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/cnxt/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/cnxt/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `cnxt`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_DIGICOLOR)`. Conditional gates include `CONFIG_ARCH_DIGICOLOR`. It lists 1 DTB targets, including `cx92755_equinox.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 145 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/cnxt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `gemini`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_GEMINI)`. Conditional gates include `CONFIG_ARCH_GEMINI`. It lists 10 DTB targets, including `gemini-dlink-dir-685.dtb`, `gemini-dlink-dns-313.dtb`, `gemini-nas4220b.dtb`, `gemini-ns2502.dtb`, `gemini-rut1xx.dtb`, `gemini-sl93512r.dtb`, `gemini-sq201.dtb`, `gemini-ssi1328.dtb`, `gemini-wbd111.dtb`, `gemini-wbd222.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 12 lines, 292 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/hisilicon/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `hisilicon`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_HI3xxx)`, `dtb-$(CONFIG_ARCH_HIP01)`, `dtb-$(CONFIG_ARCH_HIP04)`, `dtb-$(CONFIG_ARCH_HISI)`, `dtb-$(CONFIG_ARCH_HIX5HD2)`, `dtb-$(CONFIG_ARCH_SD5203)`. Conditional gates include `CONFIG_ARCH_HI3xxx`, `CONFIG_ARCH_HIP01`, `CONFIG_ARCH_HIP04`, `CONFIG_ARCH_HISI`, `CONFIG_ARCH_HIX5HD2`, `CONFIG_ARCH_SD5203`. It lists 6 DTB targets, including `hi3620-hi4511.dtb`, `hip01-ca9x2.dtb`, `hip04-d01.dtb`, `hi3519-demb.dtb`, `hisi-x5hd2-dkb.dtb`, `sd5203.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 13 lines, 318 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/hpe/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/hpe/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `hpe`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_HPE_GXP)`. Conditional gates include `CONFIG_ARCH_HPE_GXP`. It lists 1 DTB targets, including `hpe-bmc-dl360gen10.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 3 lines, 91 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/hpe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `intel`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `subdir-y`. Conditional gates include none. Subdirectory traversal includes `axm`, `ixp`, `pxa`, `socfpga`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 103 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/axm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/axm/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `axm`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_AXXIA)`. Conditional gates include `CONFIG_ARCH_AXXIA`. It lists 1 DTB targets, including `axm5516-amarillo.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 5 lines, 139 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/axm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/ixp/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/ixp/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `ixp`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_IXP4XX)`. Conditional gates include `CONFIG_ARCH_IXP4XX`. It lists 20 DTB targets, including `intel-ixp42x-actiontec-mi424wr-ac.dtb`, `intel-ixp42x-actiontec-mi424wr-d.dtb`, `intel-ixp42x-linksys-nslu2.dtb`, `intel-ixp42x-linksys-wrv54g.dtb`, `intel-ixp42x-freecom-fsg-3.dtb`, `intel-ixp42x-welltech-epbx100.dtb`, `intel-ixp42x-ixdp425.dtb`, `intel-ixp43x-kixrp435.dtb`, `intel-ixp46x-ixdp465.dtb`, `intel-ixp42x-adi-coyote.dtb`, `intel-ixp42x-ixdpg425.dtb`, `intel-ixp42x-goramo-multilink.dtb`, `intel-ixp42x-iomega-nas100d.dtb`, `intel-ixp42x-dlink-dsm-g600.dtb`, `intel-ixp42x-gateworks-gw2348.dtb`, `intel-ixp43x-gateworks-gw2358.dtb`, `intel-ixp42x-netgear-wg302v1.dtb`, `intel-ixp42x-arcom-vulcan.dtb`, `intel-ixp42x-gateway-7001.dtb`, `intel-ixp42x-usrobotics-usr8200.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 22 lines, 752 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/ixp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/pxa/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/pxa/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `pxa`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_PXA)`. Conditional gates include `CONFIG_ARCH_PXA`. It lists 6 DTB targets, including `pxa300-raumfeld-connector.dtb`, `pxa300-raumfeld-controller.dtb`, `pxa300-raumfeld-speaker-l.dtb`, `pxa300-raumfeld-speaker-m.dtb`, `pxa300-raumfeld-speaker-one.dtb`, `pxa300-raumfeld-speaker-s.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 8 lines, 262 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `socfpga`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_INTEL_SOCFPGA)`. Conditional gates include `CONFIG_ARCH_INTEL_SOCFPGA`. It lists 39 DTB targets, including `socfpga_arria5_socdk.dtb`, `socfpga_arria10_chameleonv3.dtb`, `socfpga_arria10_mercury_aa1_pe1_emmc.dtb`, `socfpga_arria10_mercury_aa1_pe1_qspi.dtb`, `socfpga_arria10_mercury_aa1_pe1_sdmmc.dtb`, `socfpga_arria10_mercury_aa1_pe3_emmc.dtb`, `socfpga_arria10_mercury_aa1_pe3_qspi.dtb`, `socfpga_arria10_mercury_aa1_pe3_sdmmc.dtb`, `socfpga_arria10_mercury_aa1_st1_emmc.dtb`, `socfpga_arria10_mercury_aa1_st1_qspi.dtb`, `socfpga_arria10_mercury_aa1_st1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_st1_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_st1_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_st1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa2_pe1_qspi.dtb`, `socfpga_cyclone5_mercury_sa2_pe1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa2_pe3_qspi.dtb`, `socfpga_cyclone5_mercury_sa2_pe3_sdmmc.dtb`, and 15 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 41 lines, 1632 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/marvell/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/marvell/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `marvell`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_MMP)`, `dtb-$(CONFIG_ARCH_ORION5X)`, `dtb-$(CONFIG_MACH_ARMADA_370)`, `dtb-$(CONFIG_MACH_ARMADA_375)`, `dtb-$(CONFIG_MACH_ARMADA_38X)`, `dtb-$(CONFIG_MACH_ARMADA_39X)`, `dtb-$(CONFIG_MACH_ARMADA_XP)`, `dtb-$(CONFIG_MACH_DOVE)`, `dtb-$(CONFIG_MACH_KIRKWOOD)`. Conditional gates include `CONFIG_ARCH_MMP`, `CONFIG_ARCH_ORION5X`, `CONFIG_MACH_ARMADA_370`, `CONFIG_MACH_ARMADA_375`, `CONFIG_MACH_ARMADA_38X`, `CONFIG_MACH_ARMADA_39X`, `CONFIG_MACH_ARMADA_XP`, `CONFIG_MACH_DOVE`, `CONFIG_MACH_KIRKWOOD`. It lists 155 DTB targets, including `pxa168-aspenite.dtb`, `pxa910-dkb.dtb`, `mmp2-brownstone.dtb`, `mmp2-olpc-xo-1-75.dtb`, `mmp3-dell-ariel.dtb`, `orion5x-kuroboxpro.dtb`, `orion5x-lacie-d2-network.dtb`, `orion5x-lacie-ethernet-disk-mini-v2.dtb`, `orion5x-linkstation-lsgl.dtb`, `orion5x-linkstation-lswtgl.dtb`, `orion5x-linkstation-lschl.dtb`, `orion5x-lswsgl.dtb`, `orion5x-maxtor-shared-storage-2.dtb`, `orion5x-netgear-wnr854t.dtb`, `orion5x-rd88f5182-nas.dtb`, `armada-370-c200-v2.dtb`, `armada-370-db.dtb`, `armada-370-dlink-dns327l.dtb`, `armada-370-mirabox.dtb`, `armada-370-netgear-rn102.dtb`, `armada-370-netgear-rn104.dtb`, `armada-370-rd.dtb`, `armada-370-seagate-nas-2bay.dtb`, `armada-370-seagate-nas-4bay.dtb`, and 131 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 165 lines, 4558 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/mediatek/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `mediatek`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_MEDIATEK)`. Conditional gates include `CONFIG_ARCH_MEDIATEK`. It lists 16 DTB targets, including `mt2701-evb.dtb`, `mt6572-jty-d101.dtb`, `mt6572-lenovo-a369i.dtb`, `mt6580-evbp1.dtb`, `mt6582-alcatel-yarisxl.dtb`, `mt6582-prestigio-pmt5008-3g.dtb`, `mt6589-aquaris5.dtb`, `mt6589-fairphone-fp1.dtb`, `mt6592-evb.dtb`, `mt7623a-rfb-emmc.dtb`, `mt7623a-rfb-nand.dtb`, `mt7623n-rfb-emmc.dtb`, `mt7623n-bananapi-bpi-r2.dtb`, `mt7629-rfb.dtb`, `mt8127-moose.dtb`, `mt8135-evbp1.dtb`.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 18 lines, 449 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/mediatek/Makefile -->
