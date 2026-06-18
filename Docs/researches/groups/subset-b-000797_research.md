# subset-b-000797 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c

### Purpose
Freescale C293 PCIe board support for the 85xx Book-E platform. It wires the C293PCIE device-tree compatible into the PowerPC machine table and supplies the minimal architecture, interrupt, PCI, SMP, and device publication hooks required for boot.

### Important APIs, Types, And Functions
Key entry points are `c293_pcie_pic_init()`, `c293_pcie_setup_arch()`, `machine_arch_initcall(c293_pcie, mpc85xx_common_publish_devices)`, and `define_machine(c293_pcie)`. The machine uses compatible string `fsl,C293PCIE`, MPIC big-endian single-destination interrupt setup, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, and the generic `mpic_get_irq` path.

### Control Flow
During platform selection, `define_machine` matches the root compatible. Setup emits progress, initializes 85xx SMP, assigns the primary PCI host bridge, and logs the board name. Later the machine initcall publishes common OF platform devices.

### State, Persistence, And Dependencies
State is firmware/device-tree supplied and kernel-global through `smp_ops`, MPIC state, and PCI host bridge setup. There is no durable persistence. It depends on OF matching, MPIC, FSL PCI helpers, and common 85xx publication.

### Integration Points
Integrates with Linux PowerPC `ppc_md`, FSL Book-E interrupt setup, PCI bridge code, and drivers bound through `mpc85xx_common_publish_devices()`.

### Risks
The file is small, but compatible-string mismatch, wrong MPIC flags, or skipped PCI/SMP calls would prevent boot, interrupts, or PCI enumeration.

### Test Signals
Boot a C293PCIE DTB, verify machine selection, MPIC interrupts, secondary CPU bring-up when configured, PCI enumeration, and OF platform device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/c293pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c

### Purpose
Shared 85xx/QorIQ platform helpers. It publishes common device-tree buses/devices and provides CPM2 and QE parallel I/O initialization glue used by multiple board files.

### Important APIs, Types, And Functions
Exports `qoriq_pm_ops` as a global PM operations pointer. `mpc85xx_common_publish_devices()` probes compatible devices including `soc`, `simple-bus`, `gianfar`, QE/CPM, SRIO, DMA, GUTS, GPIO LEDs, PCIe variants, and FMan. `mpc85xx_cpm2_pic_init()` finds `fsl,cpm2-pic`, initializes the CPM2 PIC, maps the cascade interrupt, and installs `cpm2_cascade()`. `mpc85xx_qe_par_io_init()` configures QE par_io for each `ucc_geth` child when QE support is enabled.

### Control Flow
Board files call the publish helper from `machine_arch_initcall()` or device initcall. CPM2 initialization finds the PIC node, initializes the secondary controller, maps the cascade, and sets chained IRQ handling. QE I/O initialization scans compatible nodes during board setup.

### State, Persistence, And Dependencies
State is kernel-global interrupt-domain and platform-device state plus `qoriq_pm_ops`. No persistent storage is written. Dependencies include OF platform probing, `irq_of_parse_and_map`, CPM2 PIC, QE par_io, and FSL SoC helpers.

### Integration Points
This is the common bridge between 85xx machine descriptors and normal Linux platform drivers. Board files rely on it to instantiate Ethernet, DMA, PCIe, SRIO, QE, and bus devices.

### Risks
Changing compatible lists can silently hide devices. Cascade IRQ setup must balance `of_node_put()` and must set chained handlers only after valid mappings.

### Test Signals
Boot representative 85xx boards and check OF devices, Ethernet/QE devices, CPM2 interrupt delivery, and absence of OF node leaks or failed platform probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c

### Purpose
Generic CoreNet/QorIQ 85xx machine support for many P/Q/T-series boards, including hypervisor-aware ePAPR variants. It avoids per-board source files by matching a list of compatible strings and common devices.

### Important APIs, Types, And Functions
Main functions are `corenet_gen_pic_init()`, `corenet_gen_setup_arch()`, `corenet_gen_publish_devices()`, `corenet_generic_probe()`, and `define_machine(corenet_generic)`. Device matches include `simple-bus`, mdio muxes, FPGA PIXIS/QIXIS, SRIO, PCIe generations, and QE. The probe path recognizes many board root compatibles and handles ePAPR hypervisor PIC selection through `epapr_paravirt_early_init()` and `ppc_md.get_irq`.

### Control Flow
Probe checks board compatible strings and may activate paravirtual interrupt behavior. Setup initializes SMP, PCI primary assignment, SWIOTLB for high memory, and board logging. PIC init allocates MPIC unless the hypervisor path is active.

### State, Persistence, And Dependencies
State lives in `ppc_md`, MPIC/EPAPR interrupt state, PCI host state, and OF platform devices. No persistent data is written. Dependencies include MPIC, EPAPR paravirt, FSL PCI, SWIOTLB, OF matching, and `mpc85xx_smp_init()`.

### Integration Points
Integrates many CoreNet boards with common Linux drivers without dedicated board files. It also shares `smp_85xx_ops` and common device publication patterns.

### Risks
The broad compatible list makes regressions high-impact. Hypervisor detection and interrupt-controller selection are sensitive; wrong behavior can break guests or bare-metal interrupt routing.

### Test Signals
Boot bare-metal and ePAPR guest DTBs, verify selected machine, interrupt source, SMP, PCI, SWIOTLB detection, and publication of buses listed in `of_device_ids`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/corenet_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c

### Purpose
GE Intelligent Platforms IMP3A board support. It provides MPIC setup, optional FPGA cascaded interrupt setup, primary PCI host selection, FPGA register mapping, CPU information, and machine registration.

### Important APIs, Types, And Functions
Key functions are `ge_imp3a_pic_init()`, `ge_imp3a_pci_assign_primary()`, `ge_imp3a_setup_arch()`, `ge_imp3a_show_cpuinfo()`, and `define_machine(ge_imp3a)`. It uses compatible `ge,IMP3A`, GE FPGA PIC compatibles, `fsl,mpc8540-pci`, `fsl,mpc8548-pcie`, `fsl,p2020-pcie`, and `ge,imp3a-fpga-regs`.

### Control Flow
PIC init skips secondary thread behavior for CAMP variants, allocates MPIC, initializes it, then finds and initializes the GE FPGA PIC cascade if present. Setup initializes SMP, maps FPGA registers for board information, and assigns primary PCI based on discovered bridge ranges.

### State, Persistence, And Dependencies
State includes global mapped FPGA registers, MPIC and cascaded GE PIC domains, and PCI controller selection. No durable persistence exists. Dependencies include OF resource parsing, `gef_pic_init()`, MPIC, FSL PCI, and seq_file CPU info.

### Integration Points
Connects GE-specific FPGA interrupt and metadata hardware to the generic 85xx platform and Linux PCI/interrupt subsystems.

### Risks
Board register offsets and cascade-compatible matching are hardware-specific. Incorrect PCI primary selection affects legacy I/O routing and device enumeration.

### Test Signals
Boot IMP3A, check `/proc/cpuinfo` board fields, cascaded FPGA interrupts, PCI root bridge assignment, and successful OF device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ge_imp3a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ksi8560.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ksi8560.c

### Purpose
Emerson KSI8560 board support for MPC8560-era 85xx hardware. It initializes MPIC, CPM2 pins, CPLD reset/control bits, CPU info, and platform-device publication.

### Important APIs, Types, And Functions
Important elements are `struct cpm_pin`, `ksi8560_pins[]`, `init_ioports()`, `ksi8560_pic_init()`, `ksi8560_setup_arch()`, `ksi8560_show_cpuinfo()`, and `define_machine(ksi8560)` with compatible `emerson,KSI8560`. It uses `cpm2_set_pin()`, `cpm2_clk_setup()`, `mpc85xx_cpm2_pic_init()`, and `mpc85xx_common_publish_devices()`.

### Control Flow
Architecture setup maps the CPLD node if available, applies board control values, initializes CPM2 pin mux and clocks, initializes the CPM2 PIC cascade, and logs board information. Device publication occurs from a machine device initcall.

### State, Persistence, And Dependencies
State is direct hardware register configuration in CPLD/CPM2/MPIC and global IRQ-domain state. It is not filesystem persistent. Dependencies include OF compatible lookup, CPM2, MPIC, and FSL common publication.

### Integration Points
It links legacy CPM2 serial/Ethernet pin muxing to platform drivers and cascades CPM2 interrupts into MPIC.

### Risks
Pin table mistakes can break serial, SCC/FCC, or Ethernet functions. CPLD register writes are board-specific and not discoverable at runtime.

### Test Signals
Boot KSI8560 DTB, validate CPM2 serial/Ethernet, CPM2 IRQs, CPLD-controlled reset/board functions, and displayed CPU info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ksi8560.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c

### Purpose
Freescale MPC8536 DS reference board support. It supplies minimal machine glue for MPIC, SMP, PCI, and common OF device publication.

### Important APIs, Types, And Functions
Key functions are `mpc8536_ds_pic_init()`, `mpc8536_ds_setup_arch()`, `machine_arch_initcall(mpc8536_ds, mpc85xx_common_publish_devices)`, and `define_machine(mpc8536_ds)` with compatible `fsl,mpc8536ds`. It uses `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, `fsl_pcibios_fixup_bus`, and `mpic_get_irq`.

### Control Flow
The machine descriptor matches the root compatible, setup initializes SMP and PCI and emits progress, then the arch initcall publishes common 85xx devices.

### State, Persistence, And Dependencies
Only kernel hardware-init state is affected: MPIC, SMP ops, PCI host selection, and platform devices. There is no persistent storage. Dependencies are OF, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Provides board-specific machine registration while delegating most functionality to common 85xx code and Linux PCI/OF subsystems.

### Risks
Small-file risks center on boot matching and MPIC flags. Omitting bus fixups can affect PCI resource setup.

### Test Signals
Boot with an MPC8536DS DTB, verify machine name, interrupts, PCI fixups, SMP initialization, and common OF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc8536_ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx.h

### Purpose
Local 85xx platform header declaring shared helpers used across board files while hiding optional implementation behind configuration stubs.

### Important APIs, Types, And Functions
Declares `mpc85xx_common_publish_devices()`, `mpc85xx_cpm2_pic_init()`, `mpc85xx_qe_par_io_init()`, and `mpc85xx_8259_init()`. Provides no-op inline versions when `CONFIG_CPM2`, `CONFIG_QUICC_ENGINE`, or `CONFIG_PPC_I8259` are disabled.

### Control Flow
There is no runtime control flow in the header. Compile-time configuration decides whether callers bind to real helper functions or empty inline stubs.

### State, Persistence, And Dependencies
No state is owned by this file. It depends on kernel config symbols and `__init` annotation availability.

### Integration Points
Board files include this header to call common device publication, legacy interrupt, CPM2, and QE helpers without scattering preprocessor checks.

### Risks
Prototype drift from implementations would break builds. Incorrect stubbing can mask needed hardware initialization when a board assumes optional support.

### Test Signals
Build 85xx configurations with CPM2/QE/i8259 enabled and disabled; verify board files compile in each combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_8259.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_8259.c

### Purpose
Legacy i8259 interrupt cascade support for 85xx boards that expose a CHRP-compatible interrupt controller behind MPIC.

### Important APIs, Types, And Functions
`mpc85xx_8259_init()` scans interrupt-controller nodes for compatible `chrp,iic`, initializes `i8259_init()`, maps the cascade interrupt, sets the default IRQ domain to `i8259_get_host()`, and installs `mpc85xx_8259_cascade()`. The cascade handler calls `i8259_irq()`, handles chained IRQ enter/exit, and dispatches via `generic_handle_irq()`.

### Control Flow
Board setup calls the init helper when legacy i8259 support is needed. The cascade path runs in interrupt context whenever the parent MPIC line fires.

### State, Persistence, And Dependencies
State is the i8259 IRQ domain, default IRQ domain, and chained handler data. There is no persistent data. Dependencies include OF interrupt mapping, the generic i8259 implementation, and Linux chained IRQ APIs.

### Integration Points
Bridges legacy ISA-style interrupts into MPIC-based 85xx machines and interacts with PCI/ISA devices that expect i8259 routing.

### Risks
Default-domain changes affect global IRQ mapping. A bad cascade mapping leaves legacy devices without interrupts or can create spurious interrupt storms.

### Test Signals
Boot a board with `chrp,iic`, verify legacy IRQ device operation, no spurious cascade loops, and correct `/proc/interrupts` accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c

### Purpose
Machine support for MPC8544 DS and MPC8572 DS boards. It provides MPIC setup, SMP/PCI initialization, CAMP-aware interrupt setup, and common device publication.

### Important APIs, Types, And Functions
Functions include `mpc85xx_ds_pic_init()`, `mpc85xx_ds_setup_arch()`, and two `define_machine()` descriptors: `mpc8544_ds` compatible `MPC8544DS` and `mpc8572_ds` compatible `fsl,MPC8572DS`. Both use `mpc85xx_common_publish_devices()`, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixup hooks, and `mpic_get_irq`.

### Control Flow
PIC initialization adjusts for the `fsl,MPC8572DS-CAMP` variant before allocating MPIC. Setup initializes SMP and PCI. Arch initcalls publish common 85xx platform devices for both machine descriptors.

### State, Persistence, And Dependencies
State includes MPIC IRQ state, SMP ops, PCI host controller state, and OF platform devices. Dependencies include OF machine compatibility, MPIC, FSL PCI, and common 85xx helpers. No durable storage is involved.

### Integration Points
Board descriptor glue connects DS reference boards to generic 85xx subsystems and common driver binding.

### Risks
CAMP handling and single-destination MPIC flags are sensitive for multi-core partitioned boot. Compatible strings are historical and must be preserved.

### Test Signals
Boot MPC8544DS and MPC8572DS DTBs, including CAMP when available; check interrupts, SMP, PCI, and device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c

### Purpose
Support for MPC8568 MDS, MPC8569 MDS, and P1021 MDS boards. It handles QE/UCC Ethernet details, PHY clock/reset quirks, board fixups, MPIC setup, PCI/SMP setup, and device publication.

### Important APIs, Types, And Functions
Important paths include `mpc8568_fixup_125_clock()`, `mpc8568_mds_phy_fixups()`, `mpc85xx_mds_reset_ucc_phys()`, `mpc85xx_mds_qe_init()`, `board_fixups()`, `mpc85xx_publish_devices()`, `mpc85xx_mds_pic_init()`, and machine descriptors `mpc8568_mds`, `mpc8569_mds`, and `p1021_mds`. It registers PHY fixups, manipulates QE par_io, maps GUTS, and calls `mpc85xx_common_publish_devices()`.

### Control Flow
Setup emits progress, initializes SMP, QE-specific pin and reset handling when configured, assigns PCI, and logs the board. Early arch initcalls perform PHY board fixups and publish devices. PIC setup allocates MPIC with single destination CPU semantics.

### State, Persistence, And Dependencies
State includes PHY fixup registrations, GUTS/QE register programming, MPIC state, PCI setup, and platform devices. No filesystem persistence is used. Dependencies include PHYLIB, QE, OF address/resource APIs, MPIC, and FSL PCI.

### Integration Points
This file is the bridge between MDS board hardware quirks and generic Ethernet/QE/PHY/platform drivers.

### Risks
PHY reset/clock code and par_io muxing are hardware-specific. Incorrect fixups can make Ethernet unreliable or invisible.

### Test Signals
Boot all three MDS variants, validate UCC/FEC Ethernet link, PHY clock fixups, QE pins, MPIC interrupts, PCI, and common device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c

### Purpose
QorIQ/MPC85xx power-management operations used by SMP hotplug and timebase synchronization on non-CoreNet 85xx systems.

### Important APIs, Types, And Functions
Key functions are the PM ops in `mpc85xx_pm_ops`: CPU prepare/die, IRQ mask, and `freeze_time_base`. `mpc85xx_setup_pmc()` finds compatible GUTS nodes such as `fsl,mpc8572-guts`, `fsl,p1020-guts`, `fsl,p1021-guts`, `fsl,p1022-guts`, `fsl,p1023-guts`, `fsl,p2020-guts`, and `fsl,bsc9132-guts`, maps registers, and assigns global `qoriq_pm_ops`.

### Control Flow
`mpc85xx_smp_init()` calls this helper when the CoreNet RCPM path is not enabled. Later SMP code invokes the registered callbacks during CPU bring-up, hot-unplug, and synchronized timebase transfer.

### State, Persistence, And Dependencies
State is the static mapped GUTS pointer and global `qoriq_pm_ops`. It persists for kernel lifetime but is not durable. Dependencies include FSL GUTS layout, OF matching, and SMP PM callers.

### Integration Points
This file plugs PM register operations into the generic 85xx SMP logic in `smp.c`.

### Risks
Wrong GUTS matching or bit programming can break hotplug, timebase freeze, or interrupt masking. The static mapping assumes one matching controller.

### Test Signals
Boot matching systems, exercise secondary CPU start, CPU offline/online, kexec where relevant, and verify timebase synchronization remains monotonic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c

### Purpose
Board support for multiple P1020/P1021/P1024/P1025 RDB, MBG, UTM, and PD variants. It centralizes shared MPIC, SMP, PCI, and board-specific DIU mux setup.

### Important APIs, Types, And Functions
Main functions are `mpc85xx_rdb_pic_init()` and `mpc85xx_rdb_setup_arch()`. Machine descriptors cover `fsl,P1020RDB`, `fsl,P1021RDB-PC`, `fsl,P1025RDB`, `fsl,P1020MBG-PC`, `fsl,P1020UTM-PC`, `fsl,P1020RDB-PC`, `fsl,P1020RDB-PD`, and `fsl,P1024RDB`. The setup path may map `fsl,p1022-guts`-style registers for display-related muxing and always calls SMP and PCI helpers.

### Control Flow
PIC init allocates MPIC, with CAMP-aware handling for `fsl,MPC85XXRDB-CAMP`. Setup performs progress logging, optional DIU/GUTS configuration, SMP initialization, PCI primary assignment, and board logging. Each variant publishes common devices by arch initcall.

### State, Persistence, And Dependencies
State includes MPIC, GUTS register bits, SMP ops, PCI selection, and OF platform devices. No persistent data is written. Dependencies include OF compatible checks, MPIC, GUTS, FSL PCI, and common 85xx code.

### Integration Points
Provides one implementation for a family of related reference boards so common drivers can bind to the same device-tree structures.

### Risks
Variant compatibility must remain exact. Any display mux or CAMP change can have board-wide side effects.

### Test Signals
Boot each DTB variant when available; validate machine match, interrupts, PCI, display mux behavior where configured, and common platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mvme2500.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mvme2500.c

### Purpose
Artesyn MVME2500 85xx board support. It registers a compact machine descriptor with MPIC, SMP, PCI, and common OF platform device setup.

### Important APIs, Types, And Functions
Key elements are `mvme2500_pic_init()`, `mvme2500_setup_arch()`, `machine_arch_initcall(mvme2500, mpc85xx_common_publish_devices)`, and `define_machine(mvme2500)` with compatible `artesyn,MVME2500`. It uses MPIC big-endian single-destination setup, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and `mpic_get_irq`.

### Control Flow
The machine descriptor matches the root DT compatible. Setup initializes SMP and PCI and logs the board. The arch initcall publishes common devices after core platform setup.

### State, Persistence, And Dependencies
State is limited to runtime hardware initialization: MPIC, SMP ops, PCI host configuration, and platform devices. Dependencies include OF, MPIC, FSL PCI, and common 85xx publication. No durable persistence exists.

### Integration Points
Connects MVME2500 hardware to generic 85xx kernel subsystems and PCI/platform drivers.

### Risks
Minimal glue still controls boot-critical interrupts and PCI routing. Compatible typo or MPIC flag changes can stop platform boot.

### Test Signals
Boot MVME2500 DTB, verify machine match, interrupt delivery, PCI enumeration, SMP when configured, and platform-device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mvme2500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1010rdb.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1010rdb.c

### Purpose
Freescale P1010RDB and P1010RDB-PB board support. It supplies a custom probe for two compatible strings while sharing the same MPIC, SMP, PCI, and common device flow.

### Important APIs, Types, And Functions
Important functions are `p1010_rdb_pic_init()`, `p1010_rdb_setup_arch()`, `p1010_rdb_probe()`, and `define_machine(p1010_rdb)`. The probe accepts `fsl,P1010RDB` and `fsl,P1010RDB-PB`. Setup calls `mpc85xx_smp_init()` and `fsl_pci_assign_primary()`, and the arch initcall publishes common devices.

### Control Flow
Machine selection uses the explicit probe rather than a single `.compatible` field. Once selected, setup initializes the standard 85xx subsystems and PIC init allocates MPIC.

### State, Persistence, And Dependencies
Runtime state includes MPIC, SMP ops, PCI host assignment, and OF platform devices. No persistent storage is modified. Dependencies include OF machine compatibility, MPIC, FSL PCI, and common 85xx code.

### Integration Points
The board-specific probe lets two hardware variants share the same machine descriptor and downstream driver population.

### Risks
Adding/removing accepted compatibles affects board boot. MPIC single-destination behavior and PCI fixups are boot-critical.

### Test Signals
Boot both P1010RDB variants, confirm probe success, interrupts, PCI, SMP setup, and common platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1010rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_ds.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_ds.c

### Purpose
P1022 DS reference board support with substantial DIU/display mux handling. Besides standard MPIC/SMP/PCI setup, it switches localbus/DIU pins, programs the DIU pixel clock, validates monitor ports, and disables flash nodes when framebuffer use conflicts with localbus access.

### Important APIs, Types, And Functions
Important functions are `lbc_br_to_phys()`, `p1022ds_set_monitor_port()`, `p1022ds_set_pixel_clock()`, `p1022ds_valid_monitor_port()`, `early_video_setup()`, `p1022_ds_setup_arch()`, `p1022_ds_pic_init()`, and `define_machine(p1022_ds)`. It uses static `fslfb`, `diu_ops`, GUTS, eLBC, LAW, PIXIS, and OF property update APIs.

### Control Flow
Early command-line parsing records `video=fslfb`. During setup, DIU callbacks are installed; if framebuffer use is requested, localbus flash child nodes are marked disabled before MTD drivers load. Monitor selection later maps GUTS/eLBC/LAW/PIXIS, forces localbus banks to GPCM if needed, enters indirect PIXIS mode, switches board/chip muxes, and toggles DVI/LVDS bits. Pixel-clock programming converts picoseconds to a divider and updates GUTS `clkdvdr`.

### State, Persistence, And Dependencies
State includes static `fslfb`, device-tree `status` property updates, DIU callback globals, and MMIO register changes. No disk persistence exists, but the live device tree is mutated for the boot session. Dependencies include OF, FSL GUTS/eLBC/LAW layouts, DIU framebuffer API, MPIC, FSL PCI, SWIOTLB, and 85xx SMP.

### Integration Points
Integrates the arch platform with the DIU framebuffer driver through `diu_ops`, with MTD by disabling conflicting flash nodes, and with common 85xx PCI/interrupt/device flows.

### Risks
High-risk MMIO path: wrong BR/OR/LAW interpretation, missing unmaps, or invalid OF node handling can disable flash, blank displays, or corrupt localbus timing. Device-tree mutation depends on static property lifetime.

### Test Signals
Boot with and without `video=fslfb`, verify NOR/NAND node status, DVI and LVDS output, pixel clock accuracy, flash availability when DIU is inactive, PCI, interrupts, and SWIOTLB behavior above 4G.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_rdk.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_rdk.c

### Purpose
P1022 RDK board support with DIU-specific pixel clock and monitor-port validation plus standard MPIC/SMP/PCI setup.

### Important APIs, Types, And Functions
Key functions are `p1022rdk_set_pixel_clock()`, `p1022rdk_valid_monitor_port()`, `p1022_rdk_pic_init()`, `p1022_rdk_setup_arch()`, and `define_machine(p1022_rdk)` with compatible `fsl,p1022rdk`. The DIU path maps `fsl,p1022-guts`, computes pixel-clock dividers from `fsl_get_sys_freq()`, and assigns `diu_ops`.

### Control Flow
Setup installs DIU callbacks when the framebuffer driver is built, initializes SMP, assigns PCI, and logs the board. DIU callbacks run later from the display driver to validate supported ports and program GUTS clock-divider bits.

### State, Persistence, And Dependencies
State includes global `diu_ops` callbacks and GUTS register programming. No durable persistence is used. Dependencies include OF, GUTS, DIU framebuffer support, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
The file links P1022 RDK display clocking with the generic DIU driver and links board boot to common PCI/interrupt/device publication.

### Risks
Clock-divider calculations and supported-port validation affect display stability. Missing GUTS mappings must fail gracefully without crashing boot.

### Test Signals
Boot P1022RDK, test DIU output modes, pixel clock programming, unsupported monitor handling, PCI, interrupts, SMP, and common platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1022_rdk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1023_rdb.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1023_rdb.c

### Purpose
P1023 RDB board support, including a board-specific display/control register setup in addition to standard MPIC/SMP/PCI/common device initialization.

### Important APIs, Types, And Functions
Key functions are `p1023_rdb_setup_arch()`, `p1023_rdb_pic_init()`, `machine_arch_initcall(p1023_rdb, mpc85xx_common_publish_devices)`, and `define_machine(p1023_rdb)` with compatible `fsl,P1023RDB`. It uses OF node/resource lookup, GUTS-style register mapping, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, and PCI fixups.

### Control Flow
Setup optionally finds and maps a board control node, writes display/control bits if present, then initializes SMP and PCI. PIC init allocates MPIC with big-endian single-destination behavior. Common devices are published later by initcall.

### State, Persistence, And Dependencies
State includes MMIO configuration, MPIC state, SMP ops, PCI host selection, and platform devices. No durable persistence exists. Dependencies include OF, ioremap, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Connects board control hardware with Linux display/board behavior while reusing generic 85xx boot plumbing.

### Risks
The optional MMIO setup must not assume node presence. Register bit mistakes can break board peripherals before drivers probe.

### Test Signals
Boot P1023RDB, confirm board-control writes, interrupts, PCI, SMP, and platform-device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p1023_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p2020.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p2020.c

### Purpose
Generic P2020 board support for systems lacking a single board-compatible string. It detects P2020 CPUs and provides standard MPIC/SMP/PCI/common device setup.

### Important APIs, Types, And Functions
Functions are `p2020_pic_init()`, `p2020_setup_arch()`, `p2020_probe()`, and `define_machine(p2020)`. The probe searches CPU nodes for a P2020-compatible CPU rather than relying only on root compatibility. Setup uses `mpc85xx_smp_init()` and `fsl_pci_assign_primary()`.

### Control Flow
Machine probing runs early and accepts systems with a P2020 CPU node. After selection, setup and PIC initialization follow the common 85xx path, and the arch initcall publishes common devices.

### State, Persistence, And Dependencies
State includes MPIC, SMP, PCI, and OF platform-device runtime state. No persistent storage is touched. Dependencies include OF CPU-node scanning, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Provides a fallback machine descriptor for diverse P2020-based designs while using standard platform drivers.

### Risks
CPU-based matching may select boards that need more specific quirks. Probe changes can alter machine selection precedence.

### Test Signals
Boot representative P2020 DTBs, verify correct machine selection, interrupt routing, SMP, PCI, and common device binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/p2020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ppa8548.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ppa8548.c

### Purpose
PPMC/PPA8548 board support. It registers a simple 85xx machine, publishes selected OF buses/devices, and exposes board/CPU information.

### Important APIs, Types, And Functions
Functions include `ppa8548_pic_init()`, `ppa8548_setup_arch()`, `ppa8548_show_cpuinfo()`, `declare_of_platform_devices()`, and `define_machine(ppa8548)` with compatible `ppa8548`. Local `of_bus_ids` publish `soc`, `simple-bus`, `gianfar`, and `fsl,srio`.

### Control Flow
Machine setup emits progress and logs board identity. PIC init allocates and initializes MPIC. A machine device initcall probes only the board's selected OF bus/device compatibles rather than using the full 85xx common list.

### State, Persistence, And Dependencies
Runtime state includes MPIC and platform devices. No durable state is written. Dependencies include OF platform probing, MPIC, and seq_file CPU info.

### Integration Points
Connects a legacy board to Ethernet/SRIO/simple-bus drivers through OF platform publication.

### Risks
The narrow device match list can omit needed devices if the DT evolves. CPU info fields must tolerate missing root properties.

### Test Signals
Boot PPA8548, verify MPIC interrupts, Ethernet/SRIO device creation, and `/proc/cpuinfo` board output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/ppa8548.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c

### Purpose
QEMU e500 virtual machine platform support. It supplies a compact machine descriptor for emulated FSL e500 systems with MPIC, SMP, PCI, and common OF device publication.

### Important APIs, Types, And Functions
Functions are `qemu_e500_pic_init()`, `qemu_e500_setup_arch()`, `machine_arch_initcall(qemu_e500, mpc85xx_common_publish_devices)`, and `define_machine(qemu_e500)` with compatible `fsl,qemu-e500`. It uses MPIC, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and `mpic_get_irq`.

### Control Flow
The emulated DT root compatible selects the machine. Setup initializes SMP and PCI. PIC init allocates MPIC. Common devices are published by arch initcall.

### State, Persistence, And Dependencies
State is virtual hardware initialization state: MPIC, SMP ops, PCI bridge state, and OF platform devices. No persistence exists. Dependencies include QEMU-provided device tree, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Allows the same 85xx kernel paths to run under QEMU for development and regression testing.

### Risks
Emulated device-tree assumptions can differ from real boards. PCI and interrupt regressions here may affect CI-style coverage for 85xx.

### Test Signals
Boot `qemu-system-ppc` e500 machine, verify machine selection, virtio/PCI devices, interrupts, SMP if enabled, and common device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/qemu_e500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c

### Purpose
GPIO-controlled halt support for SGY CTS1000-style QorIQ GPIO hardware. It watches a child GPIO node and triggers orderly poweroff or halt behavior from GPIO interrupt/workqueue context.

### Important APIs, Types, And Functions
Important objects are global `halt_gpio`, `child_match`, `gpio_halt_wfn()`, `gpio_halt_irq()`, `__gpio_halt_probe()`, `gpio_halt_probe()`, `gpio_halt_remove()`, `gpio_halt_match`, and `gpio_halt_driver`. It matches `fsl,qoriq-gpio` parents and `sgy,gpio-halt` child nodes.

### Control Flow
Probe finds the halt child node, requests the GPIO descriptor, converts it to an IRQ, installs an interrupt handler, and schedules work when triggered. The work function samples the GPIO and performs the halt path. Remove cancels work and releases resources through managed APIs where applicable.

### State, Persistence, And Dependencies
State includes the global GPIO descriptor, IRQ registration, and scheduled work. No durable persistence exists. Dependencies include GPIO descriptors, OF child matching, platform driver registration, IRQ APIs, and power-management/halt helpers.

### Integration Points
Hooks board-level shutdown hardware into Linux platform-driver and GPIO subsystems.

### Risks
Global `halt_gpio` means only one active instance is expected. IRQ polarity/debounce/device-tree errors can cause false shutdowns or missed halt requests.

### Test Signals
Probe with a CTS1000 DT, toggle the halt GPIO, verify IRQ/workqueue behavior, shutdown action, and clean driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/sgy_cts1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c

### Purpose
85xx/QorIQ SMP, CPU hotplug, timebase synchronization, and kexec support. It starts secondary CPUs through ePAPR spin tables or hardware threads, selects MPIC or doorbell IPIs, and binds PM callbacks into SMP operations.

### Important APIs, Types, And Functions
Key types/functions include `struct epapr_spin_table`, `mpc85xx_give_timebase()`, `mpc85xx_take_timebase()`, `smp_85xx_start_cpu()`, `smp_85xx_kick_cpu()`, `smp_85xx_ops`, hotplug `smp_85xx_cpu_offline_self()` and `qoriq_cpu_kill()`, kexec `mpc85xx_smp_kexec_cpu_down()` and `mpc85xx_smp_machine_kexec()`, and public `mpc85xx_smp_init()`.

### Control Flow
Initialization chooses MPIC IPI operations if an `open-pic` node exists, or doorbell IPIs when `CPU_FTR_DBELL` is present. It initializes RCPM or PMC PM ops, then installs timebase/hotplug/kexec callbacks. CPU bring-up maps the firmware spin table, optionally resets the core, writes PIR and entry address, flushes caches, and marks CPU state. PPC64 SMT paths may wake a sibling hardware thread from an online sibling.

### State, Persistence, And Dependencies
State includes static timebase handshake fields, global `smp_85xx_ops`, `smp_ops`, `booting_thread_hwid`, PACA CPU start flags, `kexec_down_cpus`, and PM ops. No durable persistence. Dependencies include OF CPU nodes, MPIC, doorbells, text entry addresses, cache flushes, QorIQ PM/RCPM, kexec, and CPU hotplug APIs.

### Integration Points
Used by nearly every 85xx board setup. It coordinates with firmware spin tables, power-management registers, interrupt controllers, and PowerPC core SMP/kexec code.

### Risks
High concurrency and boot-critical risk: barriers, cache flushes, spin-table endianness, timebase freeze, SMT sibling handling, and kexec CPU teardown must be exact. Failures hang secondary CPUs or corrupt timekeeping.

### Test Signals
Boot SMP 32-bit and 64-bit systems, online/offline CPUs, test kexec/crash paths, verify IPIs via MPIC and doorbell systems, and check synchronized timebase across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h

### Purpose
Local header for 85xx SMP/PM initialization declarations.

### Important APIs, Types, And Functions
Declares `mpc85xx_smp_init()` and `mpc85xx_setup_pmc()` when SMP is enabled, with an inline empty `mpc85xx_smp_init()` when `CONFIG_SMP` is disabled. It includes `linux/init.h` for `__init` annotations.

### Control Flow
No runtime control flow exists in the header. Kernel configuration selects real SMP initialization or no-op stubbing.

### State, Persistence, And Dependencies
No state is owned here. Dependencies are limited to build-time config and implementation files `smp.c` and `mpc85xx_pm_ops.c`.

### Integration Points
Board setup files call `mpc85xx_smp_init()` unconditionally while this header hides non-SMP build differences.

### Risks
Prototype mismatch or wrong stubbing can break SMP builds or create unresolved symbols in UP builds.

### Test Signals
Build 85xx with `CONFIG_SMP=y` and disabled; verify board files link and SMP setup is included only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c

### Purpose
ABB Socrates 85xx board support. It initializes MPIC, adds a Socrates FPGA PIC cascade, initializes SMP/PCI, and publishes common devices.

### Important APIs, Types, And Functions
Functions are `socrates_pic_init()`, `socrates_setup_arch()`, and `define_machine(socrates)` with compatible `abb,socrates`. It finds `abb,socrates-fpga-pic` and calls `socrates_fpga_pic_init()`. Setup calls `mpc85xx_smp_init()` and `fsl_pci_assign_primary()`.

### Control Flow
PIC init allocates MPIC and initializes it before finding and registering the FPGA interrupt controller. Setup runs standard SMP/PCI board initialization. Common devices are published by machine arch initcall.

### State, Persistence, And Dependencies
State includes MPIC domain, FPGA PIC domain/cascade, SMP ops, PCI host assignment, and OF platform devices. No persistent storage is touched. Dependencies include Socrates FPGA PIC code, OF matching, MPIC, and FSL PCI.

### Integration Points
Connects the board's FPGA interrupt controller to Linux IRQ handling and standard 85xx platform infrastructure.

### Risks
Cascade ordering matters: MPIC must be ready before FPGA PIC setup. Missing compatible nodes should not block core board boot except for dependent devices.

### Test Signals
Boot Socrates DTB, verify FPGA interrupt sources, MPIC interrupts, PCI, SMP, and common platform-device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c

### Purpose
IRQ-domain and irq_chip implementation for the Socrates board FPGA interrupt controller. It maps FPGA interrupt lines, handles masking/ack/eoi/type configuration, and cascades from a parent interrupt.

### Important APIs, Types, And Functions
Important items include `struct socrates_fpga_irq_info`, `fpga_irqs[]`, `socrates_fpga_pic_cascade()`, `socrates_fpga_pic_ack()`, `mask()`, `mask_ack()`, `unmask()`, `eoi()`, `set_type()`, `socrates_fpga_pic_chip`, `socrates_fpga_pic_host_map()`, `socrates_fpga_pic_host_xlate()`, and public `socrates_fpga_pic_init()`.

### Control Flow
Initialization maps FPGA registers from the DT node, creates a linear IRQ domain, maps the parent cascade IRQ, and installs a chained handler. When the parent IRQ fires, the cascade handler reads pending/enabled bits and dispatches child mappings. Per-IRQ operations update FPGA mask/status/type registers.

### State, Persistence, And Dependencies
State includes static IRQ metadata, mapped FPGA MMIO, IRQ domain, cached polarity/trigger configuration, and chained handler linkage. No durable persistence exists. Dependencies include OF address/IRQ parsing, irq_domain APIs, Linux irq_chip callbacks, and Socrates board register layout.

### Integration Points
Used by `socrates.c` to expose FPGA interrupt sources as normal Linux IRQs to device drivers.

### Risks
Bit numbering, type programming, and ack/mask order can create lost interrupts or interrupt storms. The xlate path must validate specifier bounds.

### Test Signals
Trigger each FPGA interrupt line, test edge/level type configuration, mask/unmask behavior, cascade parent accounting, and invalid DT interrupt specifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h

### Purpose
Header declaring the Socrates FPGA PIC initializer for board code.

### Important APIs, Types, And Functions
Declares `void __init socrates_fpga_pic_init(struct device_node *pic);`.

### Control Flow
No runtime flow is present. `socrates.c` calls the declared initializer after MPIC setup when the FPGA PIC node is found.

### State, Persistence, And Dependencies
No state is owned here. It depends on `linux/init.h` and `linux/of.h` for annotations and `struct device_node`.

### Integration Points
Connects the board machine file to the FPGA interrupt-controller implementation without exposing internal irq_chip details.

### Risks
Prototype drift from the implementation breaks builds. Calling with an unreferenced or invalid node would fail in the implementation.

### Test Signals
Build Socrates support and boot with an `abb,socrates-fpga-pic` node to confirm linkage and initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c

### Purpose
Silicon Turnkey/Storm STx GP3-8560 board support. It supplies MPIC initialization, board setup, CPU info, and common device publication.

### Important APIs, Types, And Functions
Functions are `stx_gp3_pic_init()`, `stx_gp3_setup_arch()`, `stx_gp3_show_cpuinfo()`, `declare_of_platform_devices()` through common publication, and `define_machine(stx_gp3)` with compatible `stx,gp3-8560`. It uses `mpc85xx_common_publish_devices()`, MPIC, and `udbg_progress`.

### Control Flow
Machine matching selects the board. Setup emits progress and logs board identity. PIC init allocates MPIC. The machine initcall publishes common 85xx devices.

### State, Persistence, And Dependencies
State is runtime MPIC/platform-device state and optional `/proc/cpuinfo` output. Dependencies include OF, MPIC, seq_file, and common 85xx helper code. No persistent storage is used.

### Integration Points
Connects the board to generic 85xx interrupt and platform-driver infrastructure.

### Risks
CPU info must tolerate missing model properties. Minimal board glue still controls interrupt initialization.

### Test Signals
Boot STx GP3 DTB, verify machine selection, interrupts, common device publication, and `/proc/cpuinfo` board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/stx_gp3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/t1042rdb_diu.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/t1042rdb_diu.c

### Purpose
T1042RDB DIU display support helpers. It programs CPLD and GUTS/clock registers so the DIU framebuffer can select output ports and pixel clocks on this board family.

### Important APIs, Types, And Functions
Important elements include global `cpld_node`, `t1042rdb_set_monitor_port()`, `t1042rdb_set_pixel_clock()`, `t1042rdb_valid_monitor_port()`, and the DIU ops registration path. It accesses board CPLD nodes and FSL GUTS-style clock/mux registers, using OF mapping and DIU monitor-port enums.

### Control Flow
The board/display initialization discovers the CPLD node and assigns DIU callbacks. Later, framebuffer operations call monitor-port and pixel-clock callbacks to toggle board routing and calculate/program pixel-clock divisors.

### State, Persistence, And Dependencies
State includes the retained CPLD device node reference, DIU callback globals, and MMIO register settings. No durable persistence exists. Dependencies include OF node lookup/mapping, CPLD register layout, GUTS registers, and `CONFIG_FB_FSL_DIU`.

### Integration Points
Integrates arch board-specific routing with the generic FSL DIU framebuffer driver.

### Risks
Display bring-up depends on correct board register offsets and valid node lifetime. Bad clock divisors or mux bits can blank output or affect shared pins.

### Test Signals
Boot with DIU enabled, verify supported monitor ports, pixel clock output, node cleanup, and behavior when CPLD/GUTS nodes are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/t1042rdb_diu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c

### Purpose
TQ Components TQM85xx board support. It handles MPIC, CPM2/QE I/O where configured, PCI/SMP setup, CPU info, and common platform-device publication.

### Important APIs, Types, And Functions
Key functions are `tqm85xx_pic_init()`, `tqm85xx_setup_arch()`, `tqm85xx_show_cpuinfo()`, and `define_machine(tqm85xx)` with TQM85xx-compatible matching. The setup path uses common 85xx helpers, optional CPM2/QE initialization from `mpc85xx.h`, `mpc85xx_smp_init()`, and `fsl_pci_assign_primary()`.

### Control Flow
Machine selection leads to board setup, optional communication-processor pin/IRQ initialization, SMP setup, PCI primary selection, and logging. Device publication occurs through the common 85xx init path.

### State, Persistence, And Dependencies
State is hardware register and kernel platform state for MPIC, communication processor, PCI, SMP, and OF devices. No durable persistence. Dependencies include OF, MPIC, CPM2/QE conditionals, FSL PCI, and seq_file.

### Integration Points
Bridges TQM85xx board quirks with generic 85xx communication, PCI, and platform-driver subsystems.

### Risks
Optional CPM/QE code is configuration-sensitive. Mux and IRQ setup errors can break serial/Ethernet hardware.

### Test Signals
Build with and without CPM2/QE, boot TQM85xx DTB, validate interrupts, PCI, serial/Ethernet, and CPU info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/tqm85xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c

### Purpose
P102x Tower board support. It provides shared initialization for Tower P1020/P1021-style boards, including MPIC, SMP, PCI, and common device publishing.

### Important APIs, Types, And Functions
Key functions include `twr_p102x_pic_init()`, `twr_p102x_setup_arch()`, probe or machine descriptors for Tower-compatible strings, and initcall linkage to `mpc85xx_common_publish_devices()`. It uses `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and `mpic_get_irq`.

### Control Flow
Machine matching selects the Tower board descriptor. Setup performs standard 85xx initialization and board logging. PIC init allocates MPIC, and the arch initcall publishes common platform devices.

### State, Persistence, And Dependencies
Runtime state includes MPIC, SMP ops, PCI host assignment, and OF platform devices. No persistent storage. Dependencies include OF compatible matching, MPIC, FSL PCI, and common 85xx helpers.

### Integration Points
Provides the machine layer between Tower DTBs and generic Linux platform/PCI/interrupt drivers.

### Risks
Shared board support must preserve all compatible variants. MPIC and PCI configuration are boot-critical.

### Test Signals
Boot Tower P102x DTBs, verify machine selection, interrupt delivery, PCI enumeration, SMP, and common device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/twr_p102x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c

### Purpose
X-ES MPC85xx board family support. It covers several X-ES board variants with common MPIC/SMP/PCI setup, board-specific compatible matching, and CPU info.

### Important APIs, Types, And Functions
Important functions are `xes_mpc85xx_pic_init()`, `xes_mpc85xx_setup_arch()`, board probe/matching helpers, CPU info display, and one or more `define_machine()` descriptors for X-ES compatibles. It uses MPIC, `mpc85xx_smp_init()`, `fsl_pci_assign_primary()`, PCI fixups, and common platform-device publication.

### Control Flow
Compatible matching selects the X-ES machine descriptor. Setup emits progress, initializes SMP and PCI, and logs board information. PIC setup allocates MPIC, and common devices are published through initcall.

### State, Persistence, And Dependencies
State includes MPIC, SMP ops, PCI configuration, OF platform devices, and CPU info output. No durable state. Dependencies include OF, MPIC, FSL PCI, seq_file, and common 85xx code.

### Integration Points
Allows multiple X-ES hardware designs to share standard 85xx driver binding and interrupt/PCI infrastructure.

### Risks
Family-wide matching may miss board-specific quirks. CPU info and compatible lists must remain aligned with DTS files.

### Test Signals
Boot supported X-ES DTBs, verify compatible matching, interrupts, PCI, SMP, common devices, and CPU info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/xes_mpc85xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig

### Purpose
Kconfig menu for Freescale 86xx platforms. It defines the platform family and board selections that control compilation of the 86xx board support files.

### Important APIs, Types, And Functions
Key symbols include `PPC_86xx` and board options for MPC8641 HPCN, GE PPC9A/SBC310/SBC610, MVME7100, and related 86xx support. The symbols select dependencies such as MPIC, FSL PCI, default CPU family, and board-specific options.

### Control Flow
No runtime flow. Kconfig choices drive Makefile object inclusion and architecture features at build time.

### State, Persistence, And Dependencies
State is build configuration only. Dependencies are Kconfig relationships, selected architecture features, and downstream Makefile rules.

### Integration Points
Controls whether `arch/powerpc/platforms/86xx` objects are built and which machine descriptors are available to the kernel.

### Risks
Incorrect select/depends relationships can build incomplete platform support or expose options on incompatible CPU families.

### Test Signals
Run olddefconfig/menuconfig for each 86xx board, verify expected objects compile, and confirm generated configs include MPIC/FSL PCI features when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile

### Purpose
Build rules for 86xx platform support.

### Important APIs, Types, And Functions
Always builds common 86xx objects such as `pic.o` and `common.o` when the directory is selected. Adds `mpc86xx_smp.o` for SMP and board objects based on Kconfig symbols, including MPC8641 HPCN, GE boards, and MVME7100.

### Control Flow
No runtime flow. The kernel build system expands `obj-*` variables according to configuration.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and source file names.

### Integration Points
Connects 86xx Kconfig selections to compiled machine descriptors and shared helpers.

### Risks
Missing object entries cause selected boards to compile without machine support. Stale object names break builds.

### Test Signals
Build all 86xx board configs and SMP/non-SMP variants; verify expected objects appear in the link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c

### Purpose
Common OF platform-device publication for 86xx systems.

### Important APIs, Types, And Functions
Defines `mpc86xx_common_ids[]` with compatibles such as `soc`, `simple-bus`, and `fsl,mpc8641-pcie`. `mpc86xx_common_publish_devices()` calls `of_platform_bus_probe()` with that match table.

### Control Flow
Board machine files call `mpc86xx_common_publish_devices()` from `machine_arch_initcall()` after machine setup. It walks the device tree and creates platform devices for matching buses/controllers.

### State, Persistence, And Dependencies
State is runtime platform-device registration. No durable persistence. Dependencies include OF platform APIs and compatible strings used by 86xx DTS files.

### Integration Points
Shared by GE and MVME 86xx boards to instantiate PCIe/simple-bus children and SoC devices.

### Risks
Changing the match table can hide devices or probe too much of the tree. The function assumes device tree layout follows 86xx conventions.

### Test Signals
Boot 86xx boards and verify platform devices under `soc`, `simple-bus`, and PCIe-compatible nodes are created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c

### Purpose
GE Fanuc/GE PPC9A 86xx board support. It initializes MPIC plus GE FPGA PIC cascade, SMP, PCI, board register reporting, and NEC USB PCI fixups.

### Important APIs, Types, And Functions
Key functions are `gef_ppc9a_init_irq()`, `gef_ppc9a_setup_arch()`, board revision helpers, `gef_ppc9a_show_cpuinfo()`, `gef_ppc9a_nec_fixup()`, and `define_machine(gef_ppc9a)`. It uses compatible `gef,fpga-pic-1.00` for cascaded interrupts and `DECLARE_PCI_FIXUP_HEADER()` for NEC USB.

### Control Flow
IRQ init calls `mpc86xx_init_irq()` and then initializes the FPGA PIC if the node exists. Setup initializes SMP, maps board registers, assigns primary PCI, and logs. The PCI fixup adjusts NEC USB registers only when `machine_is(gef_ppc9a)`.

### State, Persistence, And Dependencies
State includes mapped board registers, MPIC/GE PIC IRQ domains, SMP ops, PCI host assignment, and PCI config writes. No durable persistence. Dependencies include GE PIC support, OF, FSL PCI, and 86xx shared helpers.

### Integration Points
Connects GE board FPGA IRQs and USB controller quirks to standard 86xx platform infrastructure.

### Risks
PCI fixup must remain machine-gated to avoid modifying unrelated NEC devices. Board register mapping affects CPU info output.

### Test Signals
Boot PPC9A, verify FPGA interrupts, NEC USB operation, PCI enumeration, SMP, and `/proc/cpuinfo` board revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_ppc9a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c

### Purpose
GE SBC310 86xx board support. It is similar to other GE 86xx boards, combining MPIC, FPGA PIC cascade, SMP, PCI setup, board register reporting, and NEC USB fixup behavior.

### Important APIs, Types, And Functions
Functions include `gef_sbc310_init_irq()`, `gef_sbc310_setup_arch()`, board/FPGA revision helpers, `gef_sbc310_show_cpuinfo()`, PCI fixup logic, and `define_machine(gef_sbc310)`. It uses GE FPGA PIC compatible matching and FSL PCI helpers.

### Control Flow
Machine setup maps board registers, initializes SMP and primary PCI, and logs board details. IRQ init initializes MPIC and optional FPGA PIC. PCI fixup is machine-gated and writes NEC USB controller config registers.

### State, Persistence, And Dependencies
Runtime state includes mapped board register pointer, IRQ domains, PCI config changes, SMP ops, and platform devices. No durable persistence. Dependencies include OF, GE PIC, MPIC, FSL PCI, and 86xx common publication.

### Integration Points
Integrates GE board management FPGA and USB quirks with normal Linux IRQ/PCI/platform subsystems.

### Risks
Wrong board register interpretation misreports hardware; wrong cascade setup breaks FPGA interrupt consumers; ungated PCI fixup would affect non-board systems.

### Test Signals
Boot SBC310, verify FPGA interrupt children, board revision output, USB behavior, PCI enumeration, SMP, and common device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c

### Purpose
GE SBC610 86xx board support. It initializes core 86xx interrupt/SMP/PCI subsystems, maps board FPGA registers, exposes CPU info, and applies NEC USB host fixups.

### Important APIs, Types, And Functions
Important functions are `gef_sbc610_init_irq()`, `gef_sbc610_setup_arch()`, `gef_sbc610_get_pcb_rev()`, `gef_sbc610_get_board_rev()`, `gef_sbc610_get_fpga_rev()`, `gef_sbc610_show_cpuinfo()`, `gef_sbc610_nec_fixup()`, and `define_machine(gef_sbc610)`.

### Control Flow
IRQ init calls common 86xx MPIC init, finds `gef,fpga-pic`, and initializes the GE PIC cascade. Setup maps `gef,sbc610-fpga-regs`, initializes SMP, assigns PCI, and logs. The PCI fixup adjusts NEC USB registers only on this machine.

### State, Persistence, And Dependencies
State includes `sbc610_regs`, interrupt domains, PCI configuration changes, SMP ops, and platform devices. No durable data. Dependencies include OF, GE PIC, MPIC, FSL PCI, and common 86xx device publication.

### Integration Points
Provides board-management FPGA and USB-controller integration for Linux drivers on the SBC610.

### Risks
Register mapping failure changes CPU info and may hide board revision diagnostics. Interrupt cascade and PCI fixup must stay board-specific.

### Test Signals
Boot SBC610, check board/PCB/FPGA revision output, FPGA IRQ delivery, NEC USB, PCI, SMP, and OF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/gef_sbc610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h

### Purpose
Local 86xx platform header declaring shared SMP and interrupt initialization helpers.

### Important APIs, Types, And Functions
Declares `mpc86xx_smp_init()` and `mpc86xx_init_irq()`, with an inline empty `mpc86xx_smp_init()` for non-SMP builds.

### Control Flow
No runtime control flow. Build configuration decides whether the real SMP implementation is linked.

### State, Persistence, And Dependencies
No state is owned. Dependencies are compile-time `CONFIG_SMP`, `linux/init.h`, and the implementations in `mpc86xx_smp.c` and `pic.c`.

### Integration Points
Used by 86xx board files to call common interrupt and SMP setup without local ifdefs.

### Risks
Prototype mismatches break board builds. Incorrect stubbing can hide SMP initialization or create unresolved symbols.

### Test Signals
Build SMP and non-SMP 86xx configs and verify board files link cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c

### Purpose
SMP initialization for 86xx systems. It starts secondary CPUs using board/firmware release mechanisms and plugs MPIC-based IPI operations into the PowerPC SMP core.

### Important APIs, Types, And Functions
Important functions include `smp_86xx_kick_cpu()`, 86xx SMP operation structures, per-CPU setup, and public `mpc86xx_smp_init()`. It depends on MPIC SMP helpers such as `smp_mpic_probe`, `smp_mpic_message_pass`, and `mpic_setup_this_cpu`.

### Control Flow
Board setup calls `mpc86xx_smp_init()`. It installs MPIC SMP callbacks and sets `smp_ops`. CPU kick paths release secondary CPUs and mark them up through generic SMP state.

### State, Persistence, And Dependencies
State includes the `smp_ops_t` instance and CPU bring-up status. No durable persistence. Dependencies include MPIC, OF CPU descriptions, PowerPC SMP core, and interrupt setup from `pic.c`.

### Integration Points
Used by GE and MVME 86xx machine setup to enable secondary CPUs and IPIs.

### Risks
CPU-release assumptions, IPI routing, and per-CPU MPIC setup are boot-critical. Failures usually hang boot or leave CPUs offline.

### Test Signals
Boot SMP 86xx systems, verify secondary CPUs online, IPI delivery, CPU hotplug if available, and interrupt affinity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mpc86xx_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mvme7100.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mvme7100.c

### Purpose
Artesyn/Motorola MVME7100 86xx board support. It performs SMP/PCI setup, common interrupt setup, board probing, and NEC USB host-controller fixups.

### Important APIs, Types, And Functions
Key functions are `mvme7100_setup_arch()`, `mvme7100_probe()`, `mvme7100_usb_host_fixup()`, and `define_machine(mvme7100)` with compatible matching. It uses `mpc86xx_smp_init()`, `fsl_pci_assign_primary()`, `mpc86xx_init_irq()`, `mpic_get_irq`, and FSL PCI bus fixups.

### Control Flow
Probe accepts the board compatible. Setup logs progress, initializes SMP, assigns primary PCI, and logs board name. The NEC USB PCI fixup writes controller registers only when `machine_is(mvme7100)`.

### State, Persistence, And Dependencies
Runtime state includes SMP ops, MPIC state, PCI host assignment, and PCI config-space changes. No persistent storage. Dependencies include OF, MPIC, FSL PCI, and common 86xx helpers.

### Integration Points
Links MVME7100 firmware/device tree to 86xx PCI, interrupt, and platform-driver subsystems.

### Risks
The USB fixup must be board-gated. PCI fixup bus and primary assignment are required for correct device resources.

### Test Signals
Boot MVME7100, verify USB host behavior, PCI enumeration, interrupts, SMP, and common platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/mvme7100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c

### Purpose
Common MPIC initialization for 86xx boards.

### Important APIs, Types, And Functions
Public `mpc86xx_init_irq()` locates the OpenPIC interrupt controller node, allocates an MPIC with appropriate flags, initializes it, and prepares the machine for `mpic_get_irq`.

### Control Flow
Board `init_IRQ` callbacks call this helper during early boot. It maps and initializes the interrupt controller before normal device interrupts are enabled.

### State, Persistence, And Dependencies
State is MPIC allocation, mapping, and interrupt-domain state. No durable persistence. Dependencies include OF interrupt-controller lookup, MPIC APIs, and PowerPC IRQ core.

### Integration Points
Shared by all 86xx machine descriptors that use MPIC as the root interrupt controller.

### Risks
OpenPIC node matching and MPIC flags must match hardware endianness and routing. A failed allocation blocks interrupt delivery.

### Test Signals
Boot each 86xx board and verify MPIC initialization logs, timer/device interrupts, and `mpic_get_irq` operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig

### Purpose
Kconfig definitions for MPC8xx/PQ1 platforms and board options.

### Important APIs, Types, And Functions
Symbols define `PPC_8xx` platform support and boards such as MPC86xADS, MPC885ADS, TQM8xx, EP88xC, and Adder875. It also exposes feature options for CPM1, 8xx GPIO, device tree, and board-specific support.

### Control Flow
No runtime flow. Kconfig selects CPU family, interrupt, CPM, and board object build coverage.

### State, Persistence, And Dependencies
State is build configuration. Dependencies are Kconfig expressions, default selections, and Makefile object rules.

### Integration Points
Controls compilation of `arch/powerpc/platforms/8xx` machine, PIC, CPM1, and board setup files.

### Risks
Incorrect selects can build boards without required CPM/PIC support or hide valid board options.

### Test Signals
Generate configs for each 8xx board, verify expected symbols and objects, and build with/without optional GPIO and CPM features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile

### Purpose
Build rules for MPC8xx platform support.

### Important APIs, Types, And Functions
The Makefile selects shared objects such as setup, PIC, CPM1, machine check, and optional microcode patching, plus board setup objects based on Kconfig symbols.

### Control Flow
No runtime flow. Kernel build configuration expands `obj-*` entries to choose compiled files.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and source/object file names.

### Integration Points
Connects 8xx Kconfig board selections to machine descriptors and shared CPM/PIC support.

### Risks
Missing or wrong object entries produce link failures or selected boards without runtime support.

### Test Signals
Build all 8xx board configurations and optional feature combinations; verify expected objects in the link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c

### Purpose
Adder875 MPC8xx board support. It initializes board-specific CPM1 pins, platform devices, and machine callbacks for a PQ1/8xx system.

### Important APIs, Types, And Functions
The file defines a CPM pin table, an `init_ioports()` helper, board setup, platform-device publication, and a `define_machine()` descriptor. It relies on `cpm1_set_pin()`, `cpm1_clk_setup()` where needed, `mpc8xx_pic_init()`, `mpc8xx_get_irq()`, `mpc8xx_calibrate_decr()`, RTC helpers, and restart support from shared 8xx code.

### Control Flow
Machine setup applies pin muxing, initializes CPM and board peripherals, then platform devices are published from the board initcall. The machine descriptor routes interrupts through the 8xx SIU PIC.

### State, Persistence, And Dependencies
State is CPM pin/register programming, PIC state, platform devices, and board setup side effects. No durable data is written. Dependencies include OF, CPM1, 8xx PIC, and common `m8xx_setup.c` helpers.

### Integration Points
Connects board pin muxing and device-tree buses to CPM/serial/Ethernet/platform drivers.

### Risks
Pin tables are hardware-specific and easy to regress. Wrong interrupt callbacks or timebase setup prevent stable boot.

### Test Signals
Boot Adder875 DTB, verify serial/Ethernet pins, interrupts, RTC/timebase, restart path, and platform-device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c

### Purpose
Platform driver for the CPM1 interrupt controller and CPM error interrupt on MPC8xx systems.

### Important APIs, Types, And Functions
Defines `struct cpm_pic_data`, irq_chip callbacks `cpm_mask_irq()`, `cpm_unmask_irq()`, `cpm_end_irq()`, cascade helpers `cpm_get_irq()` and `cpm_cascade()`, IRQ-domain ops, `cpm_pic_probe()`, `cpm_pic_driver`, and `cpm_error_driver`. It registers via `arch_initcall(cpm_pic_init)` and `subsys_initcall(cpm_error_init)`.

### Control Flow
The CPM PIC driver probes `fsl,cpm1-pic` or legacy CPM nodes, maps registers, initializes CICR/CIMR, creates a 64-entry IRQ domain, and chains the parent IRQ. The cascade path acknowledges vector selection and dispatches mapped child IRQs. The error driver requests a no-op error IRQ handler.

### State, Persistence, And Dependencies
State includes mapped CPM PIC registers, IRQ domain, chained handler data, and requested error IRQ. No durable persistence. Dependencies include platform devices, OF matching, irq_domain, chained IRQ APIs, and CPM register definitions.

### Integration Points
Exposes CPM peripheral interrupts to Linux drivers and cascades them through the 8xx SIU interrupt system.

### Risks
Vector extraction, mask/eoi bit order, and parent IRQ mapping are interrupt-critical. The no-op error handler intentionally suppresses a known CPM race.

### Test Signals
Probe CPM PIC, trigger SCC/SMC/FEC CPM interrupts, verify mask/unmask/eoi behavior, error IRQ handling, and `/proc/interrupts` mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1-ic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c

### Purpose
Core CPM1 management for MPC8xx systems: reset, microcode loading, CPM command execution, baud-rate generator setup, pin muxing, clock routing, and optional GPIO chip registration.

### Important APIs, Types, And Functions
Exports `cpmp`, `mpc8xx_immr`, `cpm_reset()`, `cpm_command()`, `cpm_setbrg()`, `cpm1_set_pin()`, `cpm1_clk_setup()`, and optional `cpm1_gpiochip_add16()` / `cpm1_gpiochip_add32()`. Internal types model 16-bit and 32-bit CPM I/O ports and GPIO chip state with shadowed data registers and locks.

### Control Flow
`cpm_reset()` initializes CPM base pointers, resets the CPM unless early debug forbids it, optionally loads microcode, and programs SDMA priority. `cpm_command()` serializes commands with a spinlock and polls completion. Pin and clock helpers directly program CPM registers. Optional GPIO registration maps port registers, initializes chip callbacks, and maps per-pin IRQs from DT.

### State, Persistence, And Dependencies
State includes global MMIO pointers, CPM register settings, BRG settings, pin muxes, clock routing, GPIO shadow data, spinlocks, and IRQ maps. No durable persistence. Dependencies include CPM/8xx register definitions, OF IRQ, GPIO library, DMA/MM headers, and optional microcode patching.

### Integration Points
Used by 8xx board setup and CPM drivers for serial, Ethernet, and GPIO. Provides exported CPM command/BRG APIs to other kernel code.

### Risks
High hardware risk: direct MMIO, lock ordering, command polling timeout, pin numbering, and GPIO shadow writes can break multiple peripherals. There is no deallocator for CPM DP RAM by design.

### Test Signals
Exercise CPM reset, command timeout/error paths, serial baud generation, SCC/SMC/FEC pin muxes, GPIO direction/get/set/to_irq, and builds with `CONFIG_8xx_GPIO` and `CONFIG_UCODE_PATCH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/cpm1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c

### Purpose
Embedded Planet EP88xC board support for MPC8xx. It configures CPM1 pins, board-control registers, and OF platform-device publication.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `ep88xc_pins[]`, `init_ioports()`, `ep88xc_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(ep88xc)` with compatible `fsl,ep88xc`. It maps `fsl,ep88xc-bcsr`, applies CPM1 pin/clock helpers, and publishes `soc`/`simple-bus` style devices.

### Control Flow
Setup applies CPM I/O pin muxing, maps board-control registers if present, and performs board-specific initialization. A machine device initcall publishes platform devices.

### State, Persistence, And Dependencies
State includes CPM pin/clock registers, BCSR MMIO settings, PIC/timebase machine callbacks, and platform devices. No durable persistence. Dependencies include OF, CPM1, 8xx common setup, and platform probing.

### Integration Points
Connects EP88xC board pins and control registers to serial/Ethernet/platform drivers.

### Risks
Pin table and BCSR values are board-specific. Incorrect muxing can disable console or network.

### Test Signals
Boot EP88xC DTB, verify serial console, Ethernet, BCSR-controlled peripherals, interrupts, and platform-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c

### Purpose
Shared MPC8xx setup helpers for timer/decrementer calibration, RTC access, and restart.

### Important APIs, Types, And Functions
Key functions are `mpc8xx_calibrate_decr()`, `mpc8xx_set_rtc_time()`, `mpc8xx_get_rtc_time()`, and `mpc8xx_restart()`. Internal helpers include `timebase_interrupt()` and `get_freq()`.

### Control Flow
Decrementer calibration unlocks protected clock/timebase registers, forces clock divide-by-16, reads CPU frequency from the CPU node or uses a fallback, configures RTC/timebase control registers, maps the CPU timer IRQ, and requests the timebase interrupt. RTC helpers unlock, read/write, and relock keep-alive RTC registers. Restart disables IRQs, requests reset/checkstop behavior, and panics if it fails.

### State, Persistence, And Dependencies
State includes global `ppc_proc_freq`, `ppc_tb_freq`, timebase/RTC hardware registers, and requested IRQs. RTC time persists in hardware during power conditions, but the file does not write filesystem state. Dependencies include OF CPU properties, 8xx IMMR registers, IRQ mapping, RTC conversion helpers, and `mpc8xx_immr`.

### Integration Points
Machine descriptors use these callbacks for timebase, RTC, and restart behavior across 8xx boards.

### Risks
Register unlock ordering is hardware-sensitive. Incorrect frequency fallback, IRQ mapping, or restart bit handling affects system time or reset.

### Test Signals
Boot 8xx boards, verify decrementer frequency, timer interrupts, RTC read/write, and restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/m8xx_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c

### Purpose
MPC8xx machine-check exception handling.

### Important APIs, Types, And Functions
Defines `machine_check_8xx(struct pt_regs *regs)`. It inspects exception state, reports machine-check details, and decides recovery/fatal behavior according to PowerPC exception conventions.

### Control Flow
The PowerPC exception path calls this handler when an 8xx machine check occurs. It runs in exception context and returns a status to the core exception handling code.

### State, Persistence, And Dependencies
State is CPU exception register content in `pt_regs` and any diagnostic output. No durable persistence. Dependencies include PowerPC exception types and low-level register definitions.

### Integration Points
Wired through 8xx machine definitions or architecture exception tables to handle hardware faults.

### Risks
Exception-context code cannot sleep and must avoid unsafe operations. Returning the wrong recovery status can hide fatal hardware errors or unnecessarily panic.

### Test Signals
Inject or emulate machine-check conditions, verify diagnostics and expected panic/recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/machine_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c

### Purpose
CPM1 microcode patch loader for selected MPC8xx variants and errata/workload support. It writes predefined patch words and parameter changes into CPM microcode/dual-port memory during CPM reset.

### Important APIs, Types, And Functions
Defines `struct patch_params`, variant-specific `patch_params` and patch arrays under configuration/CPU conditionals, helper `cpm_write_patch()`, and public `cpm_load_patch(cpm8xx_t *cp)`. It may adjust SPI parameter RAM (`struct spi_pram`) and CPM command/register fields after loading.

### Control Flow
When `CONFIG_UCODE_PATCH` is enabled, `cpm_reset()` calls `cpm_load_patch()`. The loader selects the compiled patch parameters, writes patch words to CPM memory offsets, updates relocation vectors/parameters, and performs any protocol-specific parameter RAM initialization.

### State, Persistence, And Dependencies
State is CPM internal microcode RAM and parameter RAM for the current boot. No filesystem persistence. Dependencies include CPM1 register layout, compiled microcode arrays, CPU/board configuration, and `cpm8xx_t`.

### Integration Points
Feeds the CPM runtime used by SCC/SMC/FEC/SPI and other communication drivers after reset.

### Risks
Very high hardware-specific risk: wrong offsets, CPU variant, or endianness can break CPM peripherals broadly. Patch selection must match silicon and config.

### Test Signals
Boot with patch-enabled configs, verify CPM serial/Ethernet/SPI operation, inspect patch-specific errata behavior, and build all conditional variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/micropatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h

### Purpose
Board-specific constants for MPC86xADS support.

### Important APIs, Types, And Functions
Provides preprocessor definitions for MPC86xADS board-control register offsets, bits, and memory layout consumed by `mpc86xads_setup.c`.

### Control Flow
No runtime control flow. Constants are compiled into the board setup file.

### State, Persistence, And Dependencies
No state is owned. It depends on the board hardware layout matching the constants.

### Integration Points
Supports BCSR setup, peripheral enablement, and board-specific register manipulation in the MPC86xADS machine file.

### Risks
Incorrect constants directly affect board-control MMIO writes and can disable peripherals or reset lines.

### Test Signals
Build MPC86xADS support and boot-test board-control paths that consume these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c

### Purpose
MPC86xADS board setup. It configures CPM1 pins, maps board-control registers, publishes OF platform devices, and registers the 8xx machine descriptor.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `mpc866ads_pins[]`, `init_ioports()`, `mpc86xads_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(mpc86x_ads)` with compatible `fsl,mpc866ads`. It uses constants from `mpc86xads.h`.

### Control Flow
Setup applies CPM pin muxing, finds `fsl,mpc866ads-bcsr`, maps and writes board-control registers, and uses common 8xx callbacks for PIC, IRQ, time, RTC, and restart. Device publication occurs from a machine initcall.

### State, Persistence, And Dependencies
State includes CPM registers, BCSR MMIO settings, platform devices, and common 8xx machine state. No durable persistence. Dependencies include OF, CPM1, 8xx PIC/setup, and board constants.

### Integration Points
Connects MPC86xADS board-control and CPM pins to Linux serial/Ethernet/platform drivers.

### Risks
BCSR writes and pin muxes are board-critical. Missing BCSR node must be handled without crashing but may leave peripherals disabled.

### Test Signals
Boot MPC86xADS, verify console, Ethernet, BCSR-controlled devices, interrupts, timebase/RTC, restart, and platform-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads.h

### Purpose
Board-specific constants for MPC885ADS support.

### Important APIs, Types, And Functions
Defines board-control register offsets, bit masks, and layout values used by `mpc885ads_setup.c` for BCSR and peripheral setup.

### Control Flow
No runtime control flow. The header contributes compile-time constants only.

### State, Persistence, And Dependencies
No state is owned. Dependencies are the MPC885ADS hardware layout and the setup file's expectations.

### Integration Points
Supports board-control writes and peripheral enablement for the MPC885ADS machine descriptor.

### Risks
Wrong constants produce wrong MMIO writes and can disable critical board functions.

### Test Signals
Build MPC885ADS support and boot-test all setup paths using these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c

### Purpose
MPC885ADS board setup. It programs CPM1 pin muxing, board-control registers, optional FEC/PHY-related bits, platform-device publication, and machine callbacks.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `mpc885ads_pins[]`, `init_ioports()`, `mpc885ads_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(mpc885_ads)` with compatible `fsl,mpc885ads`. It uses `mpc885ads.h`, CPM1 helpers, OF node mapping, and shared 8xx callbacks.

### Control Flow
Setup initializes CPM pins/clocks, maps `fsl,mpc885ads-bcsr`, applies board-control values, and registers standard 8xx machine callbacks. A machine device initcall probes OF devices.

### State, Persistence, And Dependencies
State includes CPM register programming, BCSR MMIO bits, platform devices, PIC/timebase/RTC runtime state. No durable persistence. Dependencies include OF, CPM1, BCSR constants, and 8xx shared setup.

### Integration Points
Connects MPC885ADS hardware mux/control to Linux CPM, Ethernet, serial, and platform drivers.

### Risks
Pin tables and BCSR bits are board-specific. Incorrect ordering can break console or network before diagnostics are available.

### Test Signals
Boot MPC885ADS, validate serial, Ethernet/FEC, BCSR-controlled features, interrupts, RTC/timebase, restart, and platform-device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h

### Purpose
Local header declaring shared MPC8xx setup helpers.

### Important APIs, Types, And Functions
Declares `mpc8xx_calibrate_decr()`, `mpc8xx_restart()`, `mpc8xx_set_rtc_time()`, and `mpc8xx_get_rtc_time()` for board machine descriptors.

### Control Flow
No runtime flow. Board files reference these callbacks in `define_machine()` or setup paths.

### State, Persistence, And Dependencies
No state is owned. Depends on `linux/rtc.h` types and implementation in `m8xx_setup.c`.

### Integration Points
Provides common timebase, RTC, and restart callbacks to all 8xx board files.

### Risks
Prototype mismatch breaks builds; wrong callback use affects timekeeping or restart.

### Test Signals
Build all 8xx boards and boot-test decrementer, RTC, and restart callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c

### Purpose
Root interrupt-controller support for MPC8xx SIU PIC.

### Important APIs, Types, And Functions
Defines `mpc8xx_pic_host`, `mpc8xx_cached_irq_mask`, `siu_reg`, irq_chip callbacks `mpc8xx_unmask_irq()`, `mpc8xx_mask_irq()`, `mpc8xx_ack()`, `mpc8xx_end_irq()`, `mpc8xx_set_irq_type()`, public `mpc8xx_get_irq()`, IRQ-domain map/xlate ops, and `mpc8xx_pic_init()`.

### Control Flow
Initialization finds `fsl,pq1-pic` or legacy `mpc8xx-pic`, maps SIU registers, and creates a 64-entry IRQ domain. Runtime IRQ dispatch reads `sc_sivec`, filters the spurious vector, and maps hardware IRQs to Linux IRQs. Per-IRQ chip callbacks manipulate SIU mask, pending, and sense registers.

### State, Persistence, And Dependencies
State includes mapped SIU registers, cached mask bits, and the IRQ domain. No durable persistence. Dependencies include OF address parsing, irq_domain, 8xx IMMR register layout, and Linux IRQ core.

### Integration Points
Machine descriptors use `mpc8xx_pic_init()` and `mpc8xx_get_irq()` as root IRQ plumbing; CPM1 PIC cascades through it.

### Risks
Bit numbering and edge/level sense programming are interrupt-critical. Cached mask state must stay synchronized with hardware.

### Test Signals
Boot 8xx boards, trigger external IRQs, test edge/level configurations, spurious IRQ handling, CPM cascade, and mask/unmask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h

### Purpose
Header for MPC8xx PIC initialization and IRQ retrieval.

### Important APIs, Types, And Functions
Declares `mpc8xx_pic_init()` and `mpc8xx_get_irq()`.

### Control Flow
No runtime flow. Board machine descriptors reference these functions for `init_IRQ` and `get_irq`.

### State, Persistence, And Dependencies
No state is owned. Depends on `linux/irq.h` and the implementation in `pic.c`.

### Integration Points
Connects board files to the shared SIU PIC implementation.

### Risks
Prototype mismatch breaks builds or machine descriptor initialization.

### Test Signals
Build 8xx boards and verify `init_IRQ`/`get_irq` linkage at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c

### Purpose
TQM8xx board support. It configures CPM1 pin muxing, optional FEC pins based on device-tree properties, platform-device publication, and standard 8xx machine callbacks.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `tqm8xx_pins[]`, `tqm8xx_fec_pins[]`, `init_pins()`, `init_ioports()`, `tqm8xx_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(tqm8xx)` with compatible `tqc,tqm8xx`.

### Control Flow
Setup applies baseline CPM pins, conditionally applies FEC pins when a matching DT property/device indicates Ethernet use, then common machine callbacks handle PIC, timebase, RTC, and restart. Device publication occurs from a machine initcall.

### State, Persistence, And Dependencies
State includes CPM pin/clock registers, platform devices, and common 8xx runtime state. No durable persistence. Dependencies include OF properties, CPM1, 8xx PIC/setup, and platform probing.

### Integration Points
Connects TQM8xx board muxing to CPM serial/Ethernet drivers and OF platform devices.

### Risks
Conditional FEC pin logic can break Ethernet if DT properties change. Console pins must remain configured early enough.

### Test Signals
Boot TQM8xx with and without FEC nodes/properties, validate serial, Ethernet, interrupts, RTC/timebase, restart, and platform-device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig

### Purpose
Top-level PowerPC platform Kconfig aggregation and shared platform feature definitions.

### Important APIs, Types, And Functions
Sources platform submenus for powernv, pseries, chrp, 512x, 52xx, powermac, pasemi, ps3, cell, 8xx, 82xx, 83xx, 85xx, 86xx, embedded6xx, 44x, amigaone, book3s, and microwatt. Defines shared symbols such as `KVM_GUEST`, `EPAPR_PARAVIRT`, `PPC_HASH_MMU_NATIVE`, `PPC_OF_BOOT_TRAMPOLINE`, `PPC_DT_CPU_FTRS`, `PPC_SMP_MUXED_IPI`, `IPIC`, `MPIC`, `MPIC_TIMER`, `FSL_MPIC_TIMER_WAKEUP`, `PPC_EPAPR_HV_PIC`, `MPIC_MSGR`, `PPC_I8259`, RTAS/EEH/idle/TAU/QE/CPM options, and RTC helpers.

### Control Flow
No runtime flow. These symbols control compilation, architecture features, and driver availability.

### State, Persistence, And Dependencies
State is build configuration. Dependencies are cross-Kconfig selections and architecture capability relationships.

### Integration Points
This is the platform configuration hub consumed by top-level and per-platform Makefiles.

### Risks
Shared feature symbols affect many platforms; bad dependencies can create invalid builds or silently disable platform support.

### Test Signals
Run broad PowerPC config builds, verify menu visibility, selected symbols, and compile coverage for MPIC, RTAS, EEH, CPM, and platform submenus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile

### Purpose
Top-level build dispatch for PowerPC platform directories and shared platform objects.

### Important APIs, Types, And Functions
Uses `obj-$(CONFIG_...)` entries to include platform directories: powermac, chrp, 44x, 512x, 52xx, 8xx, 82xx, 83xx, 85xx, 86xx, powernv, pseries, pasemi, cell, ps3, embedded6xx, amigaone, book3s, and microwatt. It also includes shared `fsl_uli1575.o` when selected.

### Control Flow
No runtime flow. The kernel build system chooses directories and objects according to configuration symbols.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and directory Makefiles.

### Integration Points
Connects top-level PowerPC architecture builds to all platform-specific code.

### Risks
Wrong dispatch entries can exclude entire platform families or include incompatible code.

### Test Signals
Build representative configs for every platform symbol and verify expected directory object traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig

### Purpose
Kconfig option for Eyetech AmigaOne platform support.

### Important APIs, Types, And Functions
Defines `AMIGAONE`, its dependencies, help text, and selected platform features needed for the Articia S based board.

### Control Flow
No runtime flow. The symbol controls whether `amigaone/setup.o` is built.

### State, Persistence, And Dependencies
State is build configuration only. Dependencies are PowerPC platform and PCI/interrupt feature selections.

### Integration Points
Feeds the platform Makefile and enables the AmigaOne machine descriptor.

### Risks
Incorrect dependencies may expose unsupported builds or omit required PCI/interrupt support.

### Test Signals
Enable `CONFIG_AMIGAONE`, verify config dependencies and successful build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile

### Purpose
Build rule for AmigaOne platform support.

### Important APIs, Types, And Functions
Always builds `setup.o` when the directory is selected by `CONFIG_AMIGAONE`.

### Control Flow
No runtime flow. Kernel build system compiles the machine file.

### State, Persistence, And Dependencies
State is build artifact selection. Depends on the Kconfig symbol and source file name.

### Integration Points
Connects AmigaOne Kconfig selection to the platform machine descriptor implementation.

### Risks
Missing or renamed object breaks AmigaOne builds.

### Test Signals
Build with `CONFIG_AMIGAONE=y` and verify `setup.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c

### Purpose
Eyetech AmigaOne platform setup for MAI Logic Articia S based systems. It discovers PCI host bridges, initializes interrupts, reserves ISA I/O regions, handles restart, and registers the machine descriptor.

### Important APIs, Types, And Functions
Key functions are `amigaone_show_cpuinfo()`, `amigaone_add_bridge()`, `amigaone_setup_arch()`, `amigaone_discover_phbs()`, `amigaone_init_IRQ()`, `request_isa_regions()`, `amigaone_probe()`, `amigaone_restart()`, and `define_machine(amigaone)` with compatible `eyetech,amigaone`.

### Control Flow
Probe selects the platform. Setup discovers PCI host bridges compatible with `mai-logic,articia-s`, creates PCI controllers, and logs board info. IRQ init finds the interrupt controller and Articia PCI node and initializes interrupt routing. A machine device initcall reserves legacy ISA regions. Restart disables interrupts and performs the board reset sequence.

### State, Persistence, And Dependencies
State includes PCI controller objects, IRQ controller state, reserved I/O regions, and restart side effects. No durable storage. Dependencies include OF, PCI bridge APIs, interrupt setup, ioport resources, and udbg progress.

### Integration Points
Connects AmigaOne firmware/device tree to Linux PCI, ISA resource, interrupt, and machine callback infrastructure.

### Risks
Legacy PCI/ISA assumptions are fragile. Resource reservation conflicts or bridge discovery failures can break device enumeration.

### Test Signals
Boot AmigaOne, verify PCI host bridges, ISA I/O reservations, interrupts, restart, and `/proc/cpuinfo` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/amigaone/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig

### Purpose
Book3S platform feature Kconfig, currently focused on the Virtual Accelerator Switchboard user API.

### Important APIs, Types, And Functions
Defines `PPC_VAS`, which enables VAS support for user and kernel access to POWER accelerator functions such as NX compression.

### Control Flow
No runtime flow. The symbol controls compilation of `vas-api.o` and related VAS infrastructure.

### State, Persistence, And Dependencies
State is build configuration. Dependencies include Book3S platform capability and VAS/NX support.

### Integration Points
Controls whether the Book3S VAS character-device API is available to accelerator drivers.

### Risks
Incorrect dependency gating could expose VAS APIs on systems without hardware or omit them from systems needing NX acceleration.

### Test Signals
Build Book3S configs with and without `PPC_VAS`, verify object inclusion and dependent accelerator drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile

### Purpose
Build rule for Book3S VAS API support.

### Important APIs, Types, And Functions
Builds `vas-api.o` when `CONFIG_PPC_VAS` is enabled.

### Control Flow
No runtime flow. The build system includes the object according to Kconfig.

### State, Persistence, And Dependencies
State is build artifact selection. Depends on the Kconfig symbol and source file name.

### Integration Points
Connects the `PPC_VAS` option to the userspace VAS API implementation.

### Risks
Missing object inclusion disables the `/dev/crypto/nx-gzip` style API even when configured.

### Test Signals
Build with `CONFIG_PPC_VAS=y` and verify `vas-api.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c

### Purpose
Userspace API for Book3S VAS accelerators, currently NX-GZIP. It creates a character device, opens one transmit window per file descriptor, maps the paste address into userspace, handles paste faults, and updates user completion status blocks on translation errors.

### Important APIs, Types, And Functions
Key types are static `struct coproc_dev` and `struct coproc_instance`. Important functions include `get_vas_user_win_ref()`, `vas_update_csb()`, `vas_dump_crb()`, `coproc_open()`, `coproc_ioc_tx_win_open()`, `coproc_release()`, `do_fail_paste()`, `vas_mmap_fault()`, `vas_mmap_close()`, `coproc_mmap()`, `coproc_ioctl()`, `vas_register_coproc_api()`, and `vas_unregister_coproc_api()`.

### Control Flow
An accelerator driver calls `vas_register_coproc_api()` to create the char device under `crypto/`. Users open it, issue `VAS_TX_WIN_OPEN`, then `mmap()` one page at offset zero to map the paste address. Fault handling remaps active windows after migration/credit recovery or emulates failed paste by clearing CR0 EQ and advancing NIP. Translation faults call `vas_update_csb()` to copy a big-endian CSB to the saved user address and signal SIGSEGV if the address is invalid.

### State, Persistence, And Dependencies
State includes global `coproc_device`, per-file `coproc_instance`, VAS window pointers, task/pid/mm references, VMA pointers, and char-device class/cdev/device nodes. Device nodes are runtime kernel objects, not durable storage. Dependencies include VAS core ops, uapi `vas-api.h`, user copy APIs, kthread mm borrowing, signals, VM fault/remap APIs, and POWER paste instruction encoding.

### Integration Points
Bridges NX/VAS kernel drivers to userspace libraries using copy/paste instructions and `/dev/crypto/nx-gzip`.

### Risks
High ABI and lifetime risk: one window per fd, pid/mm/tgid reference handling, migration/lost-credit remapping, user CSB copy ordering, module owner references, and instruction emulation must be precise. User-visible ioctl/mmap behavior is compatibility-sensitive.

### Test Signals
Run NX-GZIP userspace open/ioctl/mmap/paste/close tests, invalid version and duplicate window tests, migration/lost-credit fault tests, invalid CSB address signal tests, module unload/register cycles, and concurrent multi-thread open/exit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/vas-api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Kconfig

### Purpose
Kconfig options for Cell Broadband Engine platform and SPU support.

### Important APIs, Types, And Functions
Defines `PPC_CELL`, `SPU_FS`, and `SPU_BASE` style symbols. These control Cell platform selection, SPU filesystem availability, and low-level SPU base support.

### Control Flow
No runtime flow. Kconfig symbols decide whether SPU core, callbacks, syscalls, and spufs-related code are compiled.

### State, Persistence, And Dependencies
State is build configuration. Dependencies include PowerPC platform capabilities, SPU hardware support, and optional filesystem/module choices.

### Integration Points
Feeds the Cell Makefile and enables low-level SPU infrastructure used by Cell/spufs code.

### Risks
Wrong dependencies can compile syscall hooks without backend spufs support or omit required SPU base code.

### Test Signals
Build Cell configs with SPU base and spufs built-in/module combinations; verify expected symbols and objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Makefile -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Makefile

### Purpose
Build rules for Cell/SPU platform support.

### Important APIs, Types, And Functions
When `CONFIG_SPU_BASE` is enabled it builds `spu_callbacks.o`, `spu_base.o`, and `spu_syscalls.o`. Additional Cell platform objects may be selected elsewhere by Kconfig.

### Control Flow
No runtime flow. The build system selects SPU support objects according to Kconfig.

### State, Persistence, And Dependencies
State is build artifact selection. Dependencies are Kconfig symbols and source filenames.

### Integration Points
Connects Cell Kconfig SPU options to exported SPU APIs, syscall callbacks, and base SPU enumeration.

### Risks
Missing SPU objects break spufs/syscall integration. Extra objects without hardware support can produce unresolved dependencies.

### Test Signals
Build Cell/SPU configurations, including module and built-in spufs cases, and verify linked objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c

### Purpose
Low-level SPU management core for Cell systems. It tracks SPUs, handles SLB and storage faults, requests class interrupts, creates SPU devices/sysfs attributes, exports management operations, and integrates crash shutdown.

### Important APIs, Types, And Functions
Exports `spu_management_ops`, `spu_priv1_ops`, `cbe_spu_info`, `force_sig_fault`, `spu_invalidate_slbs()`, `spu_associate_mm()`, `spu_64k_pages_available()`, `spu_setup_kernel_slbs()`, `spu_init_channels()`, `spu_add/remove_dev_attr*()`. Internal flows include `__spu_trap_data_seg()`, `__spu_trap_data_map()`, three class IRQ handlers, `spu_request_irqs()`, `create_spu()`, `spu_stat_show()`, crash SPU registration, `spu_shutdown()`, and `init_spu_base()`.

### Control Flow
Device init initializes per-node lists, registers the SPU bus, enumerates SPUs through `spu_management_ops`, creates each SPU object, requests class 0/1/2 IRQs, registers sysfs, adds global lists, registers crash shutdown, and initializes affinity. IRQ handlers dispatch class-specific faults/mailbox/stop/DMA callbacks while holding the register lock. SLB/data faults either load SLB entries, hash kernel pages, or call the SPU stop callback for process-context handling.

### State, Persistence, And Dependencies
State includes global SPU lists, per-node `cbe_spu_info`, locks/mutexes, per-SPU mm association, stats, IRQ registrations, sysfs devices, crash snapshots, and syscore shutdown. No durable persistence. Dependencies include SPU management/priv1 ops supplied by platform code, MMU/hash page code, IRQ APIs, sysfs/device core, kexec crash hooks, and Cell SPU register definitions.

### Integration Points
Provides the exported substrate used by spufs, Cell platform code, SPU context switching, coredump, and SPU device attributes.

### Risks
High concurrency risk: global list locking spans IRQ and sleepable contexts; SPU register locks protect fault state; crash shutdown runs in constrained contexts. Fault handling, SLB loading, and callback ordering are hardware-critical.

### Test Signals
Boot Cell/SPU systems, enumerate SPUs, run spufs workloads, generate DMA/storage/SLB faults, inspect sysfs stats, test coredump/crash shutdown, add/remove attributes, and verify suspend/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c

### Purpose
System-call callback table for SPU code. It lets SPU contexts request a restricted subset of 64-bit PowerPC syscalls through the PPE kernel.

### Important APIs, Types, And Functions
Defines `spu_syscall_table[]` from `asm/syscall_table_spu.h` and exports `spu_sys_callback(struct spu_syscall_block *s)`. The callback validates the syscall number, logs debug details, and invokes the selected syscall function with up to six arguments from the SPU syscall block.

### Control Flow
SPU support code calls `spu_sys_callback()` when an SPU issues a syscall request. Invalid syscall numbers return `-ENOSYS`; valid entries dispatch directly through the table.

### State, Persistence, And Dependencies
State is the static syscall table only. No durable persistence. Dependencies include syscall function prototypes, SPU syscall block layout, and the generated SPU syscall table.

### Integration Points
Used by spufs/SPU runtime to implement the allowed syscall ABI for SPU programs.

### Risks
This is ABI-sensitive and security-sensitive: table contents decide what SPU programs can invoke. Missing NULL checks would be dangerous if the table contains holes.

### Test Signals
Run SPU syscall tests for valid calls, disabled calls, out-of-range numbers, argument passing, and debug symbol formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_callbacks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c

### Purpose
Kernel syscall entry points and registration glue for spufs-backed SPU operations. It exposes `spu_create` and `spu_run`, delegates to registered spufs callbacks, and supports SPU coredump notes and active notifications.

### Important APIs, Types, And Functions
Important objects/functions are RCU-protected `spufs_calls`, `spufs_calls_get()`, `spufs_calls_put()`, `SYSCALL_DEFINE4(spu_create)`, `SYSCALL_DEFINE3(spu_run)`, coredump helpers, `notify_spus_active()`, `register_spu_syscalls()`, and `unregister_spu_syscalls()`. Module builds use `try_module_get()` and `module_put()` around the callback owner.

### Control Flow
spufs registers a `struct spufs_calls`. Syscalls acquire the calls pointer through the cleanup-class helper, validate file descriptors or affinity neighbor descriptors, then call `create_thread()` or `spu_run()`. Coredump and notification helpers call optional registered callbacks. Unregister clears the RCU pointer and waits for readers.

### State, Persistence, And Dependencies
State is the global RCU callback pointer and module references. No durable persistence. Dependencies include spufs, file descriptor helpers, RCU, module ownership, coredump APIs, and syscall definitions.

### Integration Points
This is the ABI bridge between userspace SPU syscalls and the spufs implementation, whether built-in or module.

### Risks
RCU/module lifetime and fd handling are critical. Incorrect unregister or owner checks could call unloaded code; syscall behavior is user ABI.

### Test Signals
Test `spu_create`/`spu_run` before registration, after registration, and during module unload; test affinity neighbor fd validation, coredump note paths, and concurrent syscall/unregister races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c -->
