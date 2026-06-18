# Research: subset-b-000628

Grouped source research for Alpha kernel platform, syscall, time/trap, linker, and library helpers in the Ceph client source tree. Each file section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_dp264.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_dp264.c

## Purpose
Board support for the DP264/Tsunami family and closely related EV6 systems: DP264, Monet, Webbrick, Clipper, and Shark. It installs Alpha machine vectors that bind Tsunami MMU/I/O, RTC, PCI, machine-check, reboot, and interrupt behavior to those systems. The source was read as part of `subset-b-000628` and contains 665 lines.

## Important APIs, Types, and Functions
Defines `dp264_mv`, `monet_mv`, `webbrick_mv`, `clipper_mv`, and `shark_mv` as `struct alpha_machine_vector` instances. Important helpers include `tsunami_update_irq_hw`, DP264 and Clipper irq-chip callbacks, `dp264_device_interrupt`, SRM vector handlers, `init_tsunami_irqs`, board-specific `*_init_irq`, PCI IRQ mappers, `monet_swizzle`, and init hooks such as `dp264_init_pci`, `monet_init_pci`, `clipper_init_pci`, and `webbrick_init_arch`.

## Control Flow
Initialization enters through the selected machine vector. `init_arch` sets up Tsunami resources, `init_irq` resets ISA DMA/PIC state, optionally replaces `alpha_mv.device_interrupt` for SRM firmware vectors, clears DIM masks, registers level IRQ chips, and then PCI setup maps each device through the fixed IdSel/pin tables. Runtime interrupts read the Tsunami Cchip DIR register, dispatch ISA bit 55 through `isa_device_interrupt`, and translate other set bits to Linux IRQs.

## State and Persistence Behavior
`cached_irq_mask` records enabled Tsunami interrupt bits and `cpu_irq_affinity[4]` records per-CPU routing; both are protected by `dp264_irq_lock`. Hardware state lives in TSUNAMI Cchip DIM/DIR CSRs, ISA DMA/PIC registers, PCI config interrupt-line values, SMC669 state, ES1888 setup, and VGA discovery. No filesystem persistence is performed.

## Dependencies
Depends on Alpha Tsunami core headers, `irq_impl.h`, `pci_impl.h`, `machvec_impl.h`, `proto.h`, ISA/PIC helpers, common PCI initialization, `SMC669_Init`, `es1888_init`, and VGA location. The vectors are consumed by Alpha setup code after platform detection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The fixed PCI IRQ tables encode board wiring; wrong IdSel, hose, or swizzle handling produces dead devices or shared IRQ storms. The mask polarity differs between systems and Clipper shifts IRQ numbers by 16, so off-by-one or offset regressions are likely. SMP affinity writes multiple DIM registers and must keep the ISA summary on the boot CPU.

## Test Signals
Build an Alpha DP264/Tsunami configuration, check that all five machine vectors link, boot under SRM and non-SRM paths where possible, enumerate PCI devices, verify `/proc/interrupts` changes when devices interrupt, exercise affinity changes on SMP, and regression-test ISA cascade/timer interrupts and built-in SCSI/ethernet routes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_dp264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_eiger.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_eiger.c

## Purpose
Machine-vector support for the Eiger EV6 plus Tsunami platform, with IRQ programming modeled after Takara but using SRM-provided PCI interrupt values. The source was read as part of `subset-b-000628` and contains 225 lines.

## Important APIs, Types, and Functions
Exports `eiger_mv` via `ALIAS_MV(eiger)`. Key routines are `eiger_update_irq_hw`, `eiger_enable_irq`, `eiger_disable_irq`, `eiger_device_interrupt`, `eiger_srm_device_interrupt`, `eiger_init_irq`, `eiger_map_irq`, and `eiger_swizzle`.

## Control Flow
Boot selects `eiger_mv`; IRQ init resets ISA DMA, installs SRM vector dispatch when needed, masks each hardware IRQ bank through I/O ports around `0x510`, initializes i8259 IRQs, and registers IRQs 16-127 as level-triggered Eiger interrupts. Runtime interrupt dispatch reads the master interrupt register at `0x500`; if no accelerated PCI bits are set, it falls back to ISA dispatch. PCI swizzling counts backplane bridges from port `0x502` before applying standard bridge swizzle rules.

## State and Persistence Behavior
`cached_irq_mask[2]` stores disabled IRQ bits for two 64-bit ranges; mask writes are persistent hardware state in Eiger/Tsunami interrupt controller ports. PCI routing state is taken from `PCI_INTERRUPT_LINE` programmed by firmware.

## Dependencies
Uses Tsunami machine-check/I/O/MMU macros, generic PCI setup, i8259 ISA helpers, PCI core config access, and Alpha machine vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The disabled-bit mask polarity is opposite DP264. Firmware IRQ values are adjusted by subtracting `0x80`; bad firmware or unexpected bridge layouts can map negative or wrong IRQs. Backplane bridge counting has hard-coded patterns.

## Test Signals
Compile with Eiger support, boot with SRM and non-SRM firmware, confirm IRQs 16-127 register, verify PCI devices keep working behind backplane bridges, and test both PCI and ISA interrupt delivery.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_eiger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_marvel.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_marvel.c

## Purpose
Marvel EV7 and IO7 platform support, including large-system interrupt routing, IO7 LSI/MSI IRQ chips, PCI hose initialization, RTC selection, and SMP call-in handling. The source was read as part of `subset-b-000628` and contains 467 lines.

## Important APIs, Types, and Functions
Defines `marvel_ev7_mv`. Important routines include `io7_device_interrupt`, `io7_get_irq_ctl`, `io7_enable_irq`, `io7_disable_irq`, `io7_redirect_irq`, `io7_redirect_one_lsi`, `io7_redirect_one_msi`, `marvel_init_io7_irqs`, `marvel_irq_noop`, `marvel_init_irq`, `marvel_map_irq`, `marvel_init_pci`, `marvel_init_rtc`, and `marvel_smp_callin`. It declares legacy, LSI, and MSI `irq_chip` structures.

## Control Flow
Device interrupts decode the vector into a partition/PE id and an IO7 IRQ number, bias past legacy ISA space, mask into the Marvel IRQ namespace, and call `handle_irq`. IRQ enable/disable locates the correct IO7 CSR, locks the IO7 IRQ lock, toggles enable bit 24, and flushes with `mb` plus readback. Init scans IO7s, redirects LSI/MSI targets, registers irq chips, initializes legacy IRQs, and then PCI setup discovers Marvel hoses.

## State and Persistence Behavior
Interrupt state is distributed across IO7 LSI/MSI control CSRs and per-IO7 locks; the kernel keeps no separate global mask beyond irq core state. Runtime platform state includes discovered IO7 structures, PCI hose resources, RTC mode, and SMP target routing.

## Dependencies
Depends on `core_marvel.h`, Marvel error handling, VGA helpers, Alpha SMP call-in hooks, generic IRQ/PIC code, PCI hose discovery, and firmware/platform discovery through HWRPB.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Vector encoding mixes PE id, LSI/MSI ranges, and legacy bias; mistakes can target nonexistent IO7s or wrong MSI control slots. The code logs and returns on invalid IO7 lookup, which can leave an IRQ masked forever. Large-system routing must avoid steering interrupts to offline CPUs or wrong partitions.

## Test Signals
Build Marvel EV7 config, validate `NR_IRQS >= MARVEL_NR_IRQS`, boot on Marvel or emulator hardware if available, enumerate all IO7s, exercise LSI and MSI interrupts, verify PCI map IRQ choices, and run SMP bring-up with interrupt delivery checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_marvel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_miata.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_miata.c

## Purpose
Machine support for Miata EV56/PYXIS systems, covering SRM vector adjustment, Pyxis IRQ initialization, PCI IRQ mapping/swizzling, audio/SuperIO setup, and reboot behavior. The source was read as part of `subset-b-000628` and contains 295 lines.

## Important APIs, Types, and Functions
Defines `miata_mv`. Key routines are `miata_srm_device_interrupt`, `miata_init_irq`, `miata_map_irq`, `miata_swizzle`, `miata_init_pci`, and `miata_kill_arch`.

## Control Flow
IRQ init swaps in a Miata-specific SRM dispatcher, initializes i8259, masks unwanted Pyxis interrupt bits, initializes ISA DMA, and requests no-op handlers for halt-switch and timer-cascade lines. PCI mapping uses a fixed IdSel table plus special USB function handling via ALI config byte `0x40`. Swizzling distinguishes root bus devices, built-in bridges, and card bridges.

## State and Persistence Behavior
Hardware state includes Pyxis interrupt masks, PIC/DMA registers, requested IRQ descriptors, PCI interrupt-line bytes, SMC669/ES1888 initialization, and a reset write to `PYXIS_RESET` during SRM restart. No persistent storage is updated.

## Dependencies
Uses CIA/Pyxis core support, `init_pyxis_irqs`, i8259 helpers, common ISA DMA, PCI config helpers, SMC669, ES1888, and Linux reboot command constants.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The SRM vector correction adds 8 for IRQs above 15 to compensate for firmware numbering. The USB special case depends on function number and a companion config read. Riser and bridge handling is intentionally limited, so unexpected bus topology can misroute interrupts.

## Test Signals
Boot Miata and MiataGL variants, verify halt switch and timer cascade IRQ requests, enumerate PCI and USB devices, trigger restart/halt/poweroff paths, and compare firmware-assigned IRQ lines with Linux `/proc/interrupts`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_miata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_mikasa.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_mikasa.c

## Purpose
Support for Mikasa/AlphaServer 1000 EV5+CIA systems, including local PCI interrupt mask programming and the Mikasa-Primo machine vector. The source was read as part of `subset-b-000628` and contains 190 lines.

## Important APIs, Types, and Functions
Defines `mikasa_primo_mv` with alias `mikasa_primo`. Important routines are `mikasa_update_irq_hw`, `mikasa_enable_irq`, `mikasa_disable_irq`, `mikasa_device_interrupt`, `mikasa_init_irq`, and `mikasa_map_irq`.

## Control Flow
Initialization optionally uses generic SRM interrupt dispatch, clears the board interrupt enable register at `0x536`, registers IRQs 16-31 with a level chip, then initializes i8259 and ISA DMA. Runtime dispatch combines board status from `0x534` with PIC status from `0xa0` and `0x20`, forwarding low bits to ISA and high bits to `handle_irq`.

## State and Persistence Behavior
`cached_irq_mask` stores enabled board IRQ bits. Hardware state is the 16-bit mask/status pair around ports `0x534/0x536`, the i8259 PIC, ISA DMA, and PCI interrupt-line configuration.

## Dependencies
Depends on CIA I/O/MMU, CIA machine-check and PCI init, common swizzle, i8259, ISA DMA, Alpha IRQ core, and fixed PCI IdSel maps.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Mask bit polarity is enabled-when-set. Mixing board summary bits with i8259 status can accidentally redispatch ISA if status reads are stale. Fixed table only covers expected SCSI, bridge, and three slots.

## Test Signals
Compile Mikasa support, boot AlphaServer 1000 hardware, verify SCSI and each PCI slot interrupt line, check ISA interrupts still dispatch, and ensure SRM/non-SRM paths use the expected interrupt handler.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_mikasa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_nautilus.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_nautilus.c

## Purpose
Nautilus/UP1000-style AMD Irongate platform support with firmware-preserved PCI IRQs, custom power/reboot handling, machine-check treatment, and PCI resource setup. The source was read as part of `subset-b-000628` and contains 295 lines.

## Important APIs, Types, and Functions
Defines `nautilus_mv`. Important routines include `nautilus_init_irq`, `nautilus_map_irq`, `nautilus_kill_arch`, Nautilus machine-check handling, resource descriptors for Irongate memory/bus numbering, and `nautilus_init_pci`.

## Control Flow
Boot initializes SRM interrupt dispatch if firmware is active, registers i8259 and ISA DMA, then PCI mapping mostly returns firmware-programmed `PCI_INTERRUPT_LINE` values with a UP1500 AGP bridge exception. PCI init builds Irongate resources and scans/claims buses. Shutdown probes the ALI southbridge PMU and writes the required PM control ports before falling back to generic behavior.

## State and Persistence Behavior
State lives in firmware-provided PCI config space, Irongate resource windows, i8259/DMA state, PMU config/port registers, and machine-check logs. The code does not persist state outside hardware registers.

## Dependencies
Depends on `core_irongate.h`, error handling, PCI resource allocation, i8259, common ISA DMA, memblock/resource registration, and Linux reboot commands.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The design trusts firmware IRQ routing; broken firmware will be preserved except for the AGP special case. Poweroff path assumes ALI southbridge PMU layout. Machine-check behavior must avoid masking real Irongate errors while tolerating platform quirks.

## Test Signals
Boot UP1000/UP1100/UP1500 variants, verify AGP IRQ correction, inspect PCI resources, exercise poweroff/restart paths, and inject or observe machine-check handling if hardware support exists.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_nautilus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_noritake.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_noritake.c

## Purpose
Noritake/Primo platform support for EV5+CIA systems with local PCI interrupt masking, SRM vector support, PCI table mapping, and bridge swizzling. The source was read as part of `subset-b-000628` and contains 276 lines.

## Important APIs, Types, and Functions
Defines `noritake_primo_mv`. Important routines are `noritake_update_irq_hw`, `noritake_enable_irq`, `noritake_disable_irq`, `noritake_device_interrupt`, `noritake_srm_device_interrupt`, `noritake_init_irq`, `noritake_map_irq`, and `noritake_swizzle`.

## Control Flow
IRQ init clears board interrupt mask, optionally installs SRM dispatch, registers level IRQs, and initializes i8259/ISA DMA. Runtime dispatch reads board summary plus PIC status, routes low bits to ISA and high bits to Linux IRQs. PCI mapping uses fixed IdSel tables and swizzling handles built-in and card PCI bridges.

## State and Persistence Behavior
`cached_irq_mask` represents enabled PCI/board IRQ bits. Hardware state is held in board I/O ports, PIC/DMA registers, and PCI configuration.

## Dependencies
Uses CIA core, i8259, ISA DMA, PCI common table lookup, standard PCI swizzling, and Alpha machine vectors.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Fixed routing tables and bridge assumptions are fragile for add-in bridge cards. SRM vector handling differs from direct hardware summary handling. Incorrect mask polarity would silence PCI lines.

## Test Signals
Build and boot Noritake/Primo, verify SCSI and PCI slot interrupts, exercise devices behind bridges, and compare SRM vector paths against direct PAL interrupt paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_noritake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rawhide.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rawhide.c

## Purpose
Rawhide platform support for multi-hose systems, with per-hose IRQ mask registers and Rawhide machine-vector registration. The source was read as part of `subset-b-000628` and contains 271 lines.

## Important APIs, Types, and Functions
Defines `rawhide_mv`. Key routines are `rawhide_update_irq_hw`, `rawhide_enable_irq`, `rawhide_disable_irq`, `rawhide_mask_and_ack_irq`, `rawhide_srm_device_interrupt`, `rawhide_init_irq`, and `rawhide_map_irq`.

## Control Flow
Init programs all hose interrupt masks, registers Rawhide IRQ chips for supported ranges, initializes i8259, and installs SRM vector dispatch. Runtime SRM dispatch converts vectors to Linux IRQs. PCI mapping uses a hose-aware table so the same IdSel/pin can map differently per controller.

## State and Persistence Behavior
`hose_irq_masks[4]` describes valid bits per hose and `cached_irq_masks[4]` holds current enabled/disabled state under `rawhide_irq_lock`. Hardware state is written through Rawhide interrupt mask I/O registers.

## Dependencies
Depends on multi-hose PCI controller structures, i8259, Alpha IRQ core, `pci_impl.h` common lookup, and Rawhide-specific I/O definitions.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The IRQ number encodes hose selection, so table or offset errors deliver devices to another hose's IRQ. Spinlock coverage is needed because multiple CPUs can update masks. Unsupported hose bits must remain masked.

## Test Signals
Boot with multiple PCI hoses, test each slot/hose combination, verify mask/ack behavior through interrupt counters, and ensure SRM vector conversion covers all assigned IRQs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rawhide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_ruffian.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_ruffian.c

## Purpose
Ruffian system support for CIA/Pyxis-style Alpha boards, including IRQ init, RTC/reboot quirks, PCI IRQ mapping, and memory bank sizing. The source was read as part of `subset-b-000628` and contains 240 lines.

## Important APIs, Types, and Functions
Defines `ruffian_mv`. Important routines include `ruffian_init_irq`, `ruffian_init_rtc`, `ruffian_kill_arch`, `ruffian_map_irq`, `ruffian_swizzle`, and `ruffian_get_bank_size`.

## Control Flow
IRQ init configures i8259 and platform IRQs, RTC init programs board-specific CMOS/RTC behavior, reboot logic drives Ruffian reset/power behavior, PCI mapping uses a fixed IdSel table, and swizzling walks bridges to produce the root-slot/pin pair. Memory sizing reads board registers by bank offset.

## State and Persistence Behavior
Platform state is in PIC/DMA, RTC/CMOS, board reset registers, PCI config space, and memory bank registers. The code does not keep persistent software state beyond init-time calculations.

## Dependencies
Uses CIA/Pyxis core support, i8259/ISA helpers, PCI config, Linux reboot command constants, machine vector registration, and common Alpha RTC hooks.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
RTC and reset behavior is board-specific and easy to regress on firmware variants. PCI swizzling assumes known bridge topology. Memory bank sizing uses low-level register offsets and can corrupt boot memory accounting if wrong.

## Test Signals
Boot Ruffian hardware, check RTC tick/time behavior, test reboot/halt/poweroff, verify all PCI slot interrupts, and compare detected memory size with firmware-reported banks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_ruffian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rx164.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rx164.c

## Purpose
RX164 platform support for a Pyxis/CIA Alpha board, with board interrupt mask programming and a fixed PCI routing table. The source was read as part of `subset-b-000628` and contains 203 lines.

## Important APIs, Types, and Functions
Defines `rx164_mv`. Key routines are `rx164_update_irq_hw`, `rx164_enable_irq`, `rx164_disable_irq`, `rx164_device_interrupt`, `rx164_init_irq`, and `rx164_map_irq`.

## Control Flow
IRQ init clears the board mask, initializes i8259/ISA DMA, and registers board IRQs as level-triggered. Runtime dispatch reads board status and PIC state, sends ISA bits to the ISA handler, and calls `handle_irq` for board PCI lines. PCI mapping translates IdSel and interrupt pin through a fixed table.

## State and Persistence Behavior
`cached_irq_mask` stores enabled board IRQ bits. Hardware state includes the board IRQ mask/status ports, i8259, ISA DMA controller, and PCI config lines.

## Dependencies
Depends on Pyxis/CIA core support, i8259 helpers, common ISA DMA, Alpha IRQ core, and PCI common table lookup.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The IRQ mask is a single word, so invalid IRQ ranges can shift undefined bits. Fixed PCI tables must match the board revision. ISA/PIC summary reads can introduce duplicate dispatch if mishandled.

## Test Signals
Compile and boot RX164, exercise PCI slot interrupts, verify i8259 ISA devices, and inspect `/proc/interrupts` before and after mask/unmask activity.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rx164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sable.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sable.c

## Purpose
Sable/Gamma and Lynx platform support, covering two related interrupt-controller layouts and the Sable-Gamma machine vector. The source was read as part of `subset-b-000628` and contains 345 lines.

## Important APIs, Types, and Functions
Defines `sable_gamma_mv`. Important symbols include `sable_update_irq_hw`, `sable_ack_irq_hw`, `sable_irq_swizzle`, `sable_init_irq`, `sable_map_irq`, `sable_lynx_enable_irq`, `sable_lynx_disable_irq`, `sable_lynx_mask_and_ack_irq`, `sable_lynx_srm_device_interrupt`, `sable_lynx_init_irq`, and `sable_lynx_init_pci`.

## Control Flow
Sable init programs board interrupt masks and acknowledgement registers, registers level IRQs, and maps PCI pins through a board table. Lynx support uses a shared lock and swizzle indirection, has its own irq-chip callbacks, and uses SRM vector dispatch. PCI init selects the proper Sable/Lynx setup before common scanning.

## State and Persistence Behavior
State includes cached mask bits, ack registers, `sable_lynx_irq_lock`, `sable_lynx_irq_swizzle`, i8259 state, and PCI routing state. The hardware mask/ack registers are the persistent runtime source of interrupt enablement.

## Dependencies
Uses T2/CIA-era Alpha I/O helpers, i8259, common PCI mapping/swizzle macros, Alpha machine vector setup, and SRM interrupt dispatch for Lynx.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Sable and Lynx have different IRQ routing and swizzling. Shared lock coverage must protect read-modify-write register updates. Incorrect ack sequencing can leave level IRQs asserted or lost.

## Test Signals
Build Sable and Lynx variants, boot both if possible, verify PCI slot and onboard interrupt delivery, stress mask/ack paths, and check SRM vector conversion on Lynx.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sx164.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sx164.c

## Purpose
SX164 board support for Pyxis-based Alpha systems, including architecture init quirks, IRQ setup, PCI mapping, and the SX164 machine vector. The source was read as part of `subset-b-000628` and contains 179 lines.

## Important APIs, Types, and Functions
Defines `sx164_mv`. Important routines are `sx164_init_irq`, `sx164_map_irq`, `sx164_init_pci`, and `sx164_init_arch`.

## Control Flow
Architecture init configures Pyxis/CIA resources and any SX164 alignment quirks. IRQ init sets up i8259 and Pyxis IRQs with selected mask bits. PCI init calls the platform PCI initialization path. Runtime interrupts are handled by the generic `pyxis_device_interrupt` selected in the machine vector, while this file supplies the board IRQ table.

## State and Persistence Behavior
State is primarily hardware state in Pyxis interrupt registers, i8259/DMA controllers, PCI config space, and scatter-gather alignment fields touched during init.

## Dependencies
Depends on Pyxis I/O macros, CIA machine-check handler, generic Pyxis IRQ support, i8259, common PCI setup, and Alpha machine vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Board-specific PCI routing is hard-coded and must match SX164 slot wiring. Init-order regressions can break Pyxis IRQ setup before device discovery. Alignment changes affect DMA mappings.

## Test Signals
Build SX164 config, boot hardware, validate PCI slot routing, verify DMA-capable devices, and confirm generic Pyxis interrupt dispatch reaches board-mapped IRQs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sx164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_takara.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_takara.c

## Purpose
Takara board support for CIA Alpha systems, including IRQ programming, SRM/non-SRM mapping differences, PCI swizzling, and PC873xx Super I/O enablement. The source was read as part of `subset-b-000628` and contains 288 lines.

## Important APIs, Types, and Functions
Defines `takara_mv`. Key routines include `takara_update_irq_hw`, `takara_enable_irq`, `takara_disable_irq`, `takara_device_interrupt`, `takara_srm_device_interrupt`, `takara_init_irq`, `takara_map_irq_srm`, `takara_map_irq`, `takara_swizzle`, and `takara_init_pci`.

## Control Flow
IRQ init initializes i8259, optionally installs SRM dispatch, otherwise reprograms the master control register at `0x500`, masks all 16-IRQ banks through ports around `0x510`, registers IRQs 16-127, and initializes ISA DMA. PCI init may switch to the SRM IRQ mapper, calls CIA PCI init, probes PC873xx, and enables IDE.

## State and Persistence Behavior
`cached_irq_mask[2]` stores disabled IRQ bits for two ranges. Hardware state includes ports `0x500/0x510`, i8259/DMA, PCI interrupt-line configuration, and PC873xx Super I/O configuration.

## Dependencies
Uses CIA core, i8259, ISA DMA, PCI common lookup, `pc873xx.h`, and Alpha machine vector setup.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The SRM mapper has bridge-relative IRQ additions that differ from non-SRM mapping. The swizzler warns that card bridges behind built-in bridges are unsupported. Control-register programming can switch accelerated interrupt behavior unexpectedly.

## Test Signals
Boot Takara with SRM and non-SRM paths, verify PC873xx probe and IDE enablement, test devices in native and bridged slots, and confirm IRQ banks above 64 work.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_takara.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_titan.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_titan.c

## Purpose
Titan/Privateer/Falcon/Granite EV6+Titan platform support with SMP-aware IRQ routing, legacy IRQ setup, Titan dispatch helpers, and family machine vectors. The source was read as part of `subset-b-000628` and contains 423 lines.

## Important APIs, Types, and Functions
Defines `titan_mv` and `privateer_mv`. Important routines are `titan_update_irq_hw`, `titan_enable_irq`, `titan_disable_irq`, `titan_cpu_set_irq_affinity`, `titan_set_irq_affinity`, `titan_device_interrupt`, `titan_srm_device_interrupt`, `init_titan_irqs`, `titan_init_irq`, `titan_legacy_init_irq`, `titan_dispatch_irqs`, `titan_request_irq`, `titan_late_init`, `titan_map_irq`, and `titan_init_pci`.

## Control Flow
IRQ init selects SRM or placeholder interrupt dispatch, clears Titan Cchip DIM masks, and registers Titan level IRQs. Legacy init additionally resets DMA/PIC state. Affinity updates rebuild per-CPU DIM masks with ISA routed to the boot CPU. `titan_dispatch_irqs` receives a hardware mask, filters it for the current CPU, converts highest-priority bits to SRM-like vectors, and re-enters `alpha_mv.device_interrupt`.

## State and Persistence Behavior
`titan_cpu_irq_affinity[4]` and `titan_cached_irq_mask` are protected by `titan_irq_lock`. Hardware state lives in Titan Cchip DIM CSRs, legacy PIC/DMA registers, requested IRQ descriptors for event-counting no-op handlers, and PCI hose resources.

## Dependencies
Depends on `core_titan.h`, Titan error handling, Alpha SMP masks, i8259/DMA helpers, common PCI setup, and machine-vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
`titan_device_interrupt` is a placeholder unless SRM or another dispatch path is installed. Affinity and dispatch priority conversions can misroute or starve IRQs. Legacy vs non-legacy initialization must match the selected board vector.

## Test Signals
Build Titan and Privateer vectors, boot with SRM dispatch, exercise SMP IRQ affinity, inspect `/proc/interrupts` event counts, test PCI devices across hoses, and confirm legacy ISA interrupts only when using the legacy path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_titan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_wildfire.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_wildfire.c

## Purpose
Wildfire large-system platform support with QBB/PCA-aware interrupt masks, per-PCA IRQ registration, vector decoding, PCI routing, and machine-vector registration. The source was read as part of `subset-b-000628` and contains 341 lines.

## Important APIs, Types, and Functions
Defines `wildfire_mv`. Key routines are `wildfire_update_irq_hw`, `wildfire_init_irq_hw`, `wildfire_enable_irq`, `wildfire_disable_irq`, `wildfire_mask_and_ack_irq`, `wildfire_init_irq_per_pca`, `wildfire_init_irq`, `wildfire_device_interrupt`, and `wildfire_map_irq`.

## Control Flow
Init clears or synchronizes interrupt enable registers for each possible PCA, initializes i8259, then iterates existing QBBs and PCAs to register local ISA, summary, SCSI, and PCI IRQ ranges. Runtime vectors encode source QBB, PCA, and IRQ-in-PCA; dispatch converts from PAL vector to the Linux IRQ and calls `handle_irq`.

## State and Persistence Behavior
`cached_irq_mask` is indexed by QBB/PCA and protected by `wildfire_irq_lock`; `doing_init_irq_hw` suppresses nonexistent-PCA diagnostics during bulk init. Hardware state is in PCA interrupt enable/target registers and PIC/DMA state.

## Dependencies
Depends on `core_wildfire.h` topology macros, i8259 helpers, Alpha IRQ core, PCI common lookup, and machine vector setup.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
IRQ numbers carry topology bits; wrong shifts or nonexistent PCA handling breaks all interrupts for a quadrant. Low ISA IRQs use i8259 callbacks in addition to Wildfire masks. Only known PCA bit ranges are registered.

## Test Signals
Boot Wildfire with multiple QBB/PCA combinations, verify each PCA's IRQ range, exercise ISA summary and PCI slot lines, test mask/ack under load, and inspect diagnostics for nonexistent PCA references.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_wildfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/syscalls/Makefile

## Purpose
Kbuild fragment that generates Alpha syscall UAPI and kernel syscall-table headers from `syscall.tbl`. The source was read as part of `subset-b-000628` and contains 32 lines.

## Important APIs, Types, and Functions
Defines `kapi`, `uapi`, `syscall`, `syshdr`, `systbl`, command templates `cmd_syshdr` and `cmd_systbl`, generated targets `unistd_32.h` and `syscall_table.h`, and the `all` phony target.

## Control Flow
During the arch header generation phase, Kbuild creates generated include directories, runs `scripts/syscallhdr.sh --emit-nr` for the UAPI syscall numbers, runs `scripts/syscalltbl.sh` for the internal syscall table, records both paths in target lists, and makes `all` depend on both generated headers.

## State and Persistence Behavior
The persistent outputs are generated headers under `arch/$(SRCARCH)/include/generated/{uapi,}asm`. The source-of-truth state is `syscall.tbl`; this Makefile itself has no runtime state.

## Dependencies
Depends on Kbuild variables, `CONFIG_SHELL`, `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, `syscall.tbl`, and the generated include tree consumed by `systbls.S` and UAPI users.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Incorrect paths or target prefixes break incremental rebuilds and leave stale syscall tables. Header generation must remain synchronized with `syscall.tbl`, or syscall numbers and `sys_call_table` entries drift.

## Test Signals
Run `make ARCH=alpha headers_install` or an Alpha build, touch `syscall.tbl` and verify both generated headers rebuild, and inspect that `asm/unistd_32.h` and `asm/syscall_table.h` contain matching syscall numbers/entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/systbls.S -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/systbls.S

## Purpose
Defines the Alpha kernel system call dispatch table as assembly data generated from `asm/syscall_table.h`. The source was read as part of `subset-b-000628` and contains 15 lines.

## Important APIs, Types, and Functions
Exports global `sys_call_table`. Defines `__SYSCALL(nr, entry)` as a `.quad entry` expansion before including the generated syscall table header.

## Control Flow
At assembly time, `asm/unistd.h` and generated `asm/syscall_table.h` are included. Each generated `__SYSCALL` line emits one 64-bit function pointer into the aligned `.data` table. The low-level syscall entry path indexes this table by syscall number.

## State and Persistence Behavior
The table is static kernel data in the final image. Its contents persist for the running kernel and are derived from generated headers, not modified by this file at runtime.

## Dependencies
Depends on the syscall header generation Makefile, `syscall.tbl`, low-level syscall entry code, and all syscall implementation symbols referenced by the generated table.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Any mismatch between syscall numbers, table order, and entry code ABI is catastrophic. Missing generated headers or missing syscall symbols fail the build; wrong entries misdispatch user syscalls.

## Test Signals
Build `arch/alpha/kernel/systbls.o`, inspect generated `syscall_table.h`, boot userspace smoke tests for basic syscalls, and compare `__NR_*` values with table indexes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/systbls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/termios.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/termios.c

## Purpose
Alpha-specific conversion between legacy `struct termio` user ABI and internal `struct ktermios`. The source was read as part of `subset-b-000628` and contains 56 lines.

## Important APIs, Types, and Functions
Provides `user_termio_to_kernel_termios` and `kernel_termios_to_user_termio` from `linux/termios_internal.h`.

## Control Flow
`user_termio_to_kernel_termios` copies a user `termio`, preserves high 16 bits of existing termios flags, maps low 16-bit flags and line discipline, and remaps control characters depending on canonical mode. The reverse function zeroes a `termio`, copies current flags/line, maps control characters with the same canonical VEOF/VEOL versus VMIN/VTIME split, and copies to userspace.

## State and Persistence Behavior
No persistent state is stored. The functions mutate the supplied `ktermios` or user `termio` buffers and may fault during user copy.

## Dependencies
Depends on `copy_from_user`, `copy_to_user`, `memset`, termios control-character indexes, `ICANON`, and errno semantics.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
`termios->c_line` is assigned using a mask derived from `c_lflag` in the input path, which is unusual and should be preserved only if ABI-compatible. Incorrect canonical-mode remapping changes blocking terminal behavior. User copy return handling must map faults to `-EFAULT` consistently.

## Test Signals
Run tty ioctl tests for `TCGETA`/`TCSETA`, canonical and non-canonical modes, invalid user pointers, and round-trip control-character conversion on Alpha compat ABI.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/termios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/time.c

## Purpose
Alpha clocksource, clockevent, RTC timer, QEMU virtual timer, IRQ work, and CPU cycle-frequency calibration code. The source was read as part of `subset-b-000628` and contains 463 lines.

## Important APIs, Types, and Functions
Exports `rtc_lock`, defines `est_cycle_freq`, `arch_irq_work_raise`, `rtc_timer_interrupt`, `common_init_rtc`, `time_init`, and SMP `init_clockevent`. Internal APIs include `rpcc`, per-CPU `cpu_ce`, RTC/QEMU clockevent setup, `qemu_cs`, `clocksource_rpcc`, `validate_cc_value`, `calibrate_cc_with_pit`, and `rpcc_after_update_in_progress`.

## Control Flow
Normal boot calibrates RPCC via PIT or CMOS update windows, validates against CPU-family bounds, compares with HWRPB `cycle_freq`, registers RPCC as a clocksource on single-CPU non-WTINT builds, initializes the platform RTC, and registers a periodic RTC clockevent. QEMU boots instead register a QEMU clocksource, one-shot alarm clockevent, and QEMU timer IRQ. Timer interrupts call the clockevent handler and drain pending irq_work.

## State and Persistence Behavior
Persistent runtime state includes `rtc_lock`, `est_cycle_freq`, per-CPU `clock_event_device` instances, optional per-CPU `irq_work_pending`, RTC CMOS frequency/control registers, PIT channels, QEMU alarm state, and registered clocksource/clockevent objects.

## Dependencies
Depends on RTC CMOS macros, PIT I/O ports, Alpha HWRPB, `__builtin_alpha_rpcc`, clocksource/clockchips core, IRQ work, profile/interrupt infrastructure, and platform hooks `alpha_mv.init_rtc` and `init_rtc_irq`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Cycle calibration is sensitive to broken PIT/RTC hardware, CPU-family bounds, SMP RPCC skew, and WTINT stopping counters. Wrong RTC frequency programming breaks scheduler ticks. QEMU and hardware paths have different clockevent modes.

## Test Signals
Boot Alpha hardware and QEMU, inspect registered clocksource/clockevent, verify jiffies/timer interrupts advance at `CONFIG_HZ`, test irq_work execution from timer interrupt, compare calibrated frequency with HWRPB, and run timekeeping drift tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/traps.c

## Purpose
Alpha trap initialization and core exception handlers for arithmetic traps, instruction faults, debug traps, kernel/user unaligned accesses, stack/register dumps, and PAL entry registration. The source was read as part of `subset-b-000628` and contains 929 lines.

## Important APIs, Types, and Functions
Provides `dik_show_regs`, `show_stack`, `die_if_kernel`, `do_entArith`, `do_entIF`, `do_entDbg`, `do_entUna`, `do_entUnaUser`, and `trap_init`. Exports or defines FP emulation hooks `alpha_fp_emul_imprecise` and `alpha_fp_emul` when math emulation is modular/absent. Uses `struct allregs`, `struct unaligned_stat`, and the `unaligned[2]` counters.

## Control Flow
Trap init writes the kernel global pointer to PALcode and registers entry points with `wrent`. Arithmetic traps optionally invoke FP emulation before sending `SIGFPE`. Instruction faults handle FEN re-enable, kernel bug/wtint special cases, user breakpoints/gentraps, and SIGILL/SIGTRAP/SIGFPE delivery. Kernel unaligned traps emulate selected loads/stores or forward to exception-table fixups; user unaligned traps honor UAC flags, emulate integer and FP load/store opcodes, and otherwise send SIGSEGV or SIGBUS.

## State and Persistence Behavior
Runtime state includes unaligned access counters/last addresses, current task thread flags/status, FP emulation function pointers, PAL entry vectors, signal delivery state, exception-table fixups, and diagnostic printk output. No filesystem persistence is performed.

## Dependencies
Depends on Alpha PAL entry assembly symbols, `pt_regs`, signal helpers, ptrace breakpoint logic, exception tables, FP register helpers, uaccess, HWRPB/sysinfo, scheduler/task structures, and memory-map locking for user fault classification.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Trap handlers run in fragile contexts; incorrect PC adjustment or register offset mapping can corrupt user state. User unaligned emulation is intentionally slow and must avoid reading past user mappings. Kernel unaligned fixup must preserve exception-table semantics. Signal codes are ABI-visible.

## Test Signals
Run Alpha boot smoke tests, ptrace breakpoint tests, deliberate illegal instruction/gentrap cases, user unaligned access tests with UAC flags, FP load/store unaligned tests, exception-table copy fault tests, and kernel oops stack-dump validation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/vmlinux.lds.S

## Purpose
Alpha linker script defining the final kernel image layout, entry point, ELF format, load program headers, section order, and debug/discard handling. The source was read as part of `subset-b-000628` and contains 78 lines.

## Important APIs, Types, and Functions
Sets `OUTPUT_FORMAT("elf64-alpha")`, `OUTPUT_ARCH(alpha)`, `ENTRY(__start)`, `PHDRS`, `jiffies = jiffies_64`, and layout symbols such as `_text`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_data`, `_edata`, and `_end`.

## Control Flow
The linker starts the image at either the legacy or normal Alpha kernel virtual address, emits text/fixup/warning sections, places `swapper_pg_dir`, emits read-only data, init text/data, percpu data, aligned RW data, GOT/sdata, BSS, mdebug/note, debug metadata, module info, ELF details, and generic discard rules.

## State and Persistence Behavior
The output is persistent link-time structure in `vmlinux`: symbol addresses, section boundaries, init-memory lifetime, page-directory placement, and debug/note sections. It has no runtime control flow.

## Dependencies
Depends on `asm-generic/vmlinux.lds.h`, Alpha thread/cache/page/setup constants, `CONFIG_ALPHA_LEGACY_START_ADDRESS`, `SWAPPER_PGD`, and section macros emitted by compiler/assembler sources.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Address or alignment changes can break early boot, PAL expectations, init memory freeing, percpu access, or page-table placement. Missing `.fixup`/exception-related sections can break fault recovery. Program headers must satisfy bootloader expectations.

## Test Signals
Build `vmlinux`, inspect `readelf -lS` and `nm` for expected entry/address symbols, boot both legacy and normal start configurations, and verify init memory is freed without corrupting aligned `init_task`/percpu data.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/Makefile

## Purpose
Kbuild library manifest for Alpha-specific runtime helper objects, selecting generic, EV6, and EV67 implementations. The source was read as part of `subset-b-000628` and contains 46 lines.

## Important APIs, Types, and Functions
Sets `asflags-y`, feature prefixes `ev6-$(CONFIG_ALPHA_EV6)` and `ev67-$(CONFIG_ALPHA_EV67)`, populates `lib-y`, and defines special assembly flags for divide/remainder objects built from `divide.S` or `ev6-divide.S`.

## Control Flow
Kbuild resolves CPU feature prefixes, adds objects for division, delays, memory/string, checksum, user-copy, page-copy, FP register, SRM callback/printing, and bit-scan helpers, then builds four divide/remainder objects from one selected source with `-DDIV`, `-DREM`, and `-DINTSIZE` combinations.

## State and Persistence Behavior
The persistent outputs are Alpha `lib.a`/built-in objects selected at build time. No runtime state is represented here.

## Dependencies
Depends on Kbuild, Alpha config symbols, corresponding `.S`/`.c` files, and exported helper symbols consumed across the kernel and modules.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Wrong EV6/EV67 prefix selection can link duplicate or missing symbols. Divide-object flag combinations must match ABI names. Assembly flags must include kernel C flags for symbol/ABI compatibility.

## Test Signals
Build Alpha configs for generic, EV6, and EV67; run `nm` for expected helper symbols; verify no duplicate `memcpy`/`memset`/copy-user exports; and build modules requiring exported checksum and memory helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/callback_srm.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/callback_srm.S

## Purpose
Assembly wrappers for SRM console callback functions and SRM fixup dispatch, with generic fallback stubs when SRM is unavailable. The source was read as part of `subset-b-000628` and contains 109 lines.

## Important APIs, Types, and Functions
Defines `srm_fixup`, `callback_puts`, `callback_open`, `callback_close`, `callback_read`, `callback_open_console`, `callback_close_console`, `callback_getenv`, `callback_setenv`, `callback_getc`, `callback_reset_term`, `callback_term_int`, `callback_term_ctl`, `callback_process_keycode`, `callback_ioctl`, `callback_write`, `callback_reset_env`, `callback_save_env`, `callback_pswitch`, and `callback_bios_emul`. Exports `callback_getenv`, `callback_setenv`, and `callback_save_env`; weakly defines `alpha_using_srm` and `callback_init_done` defaults.

## Control Flow
Callbacks load the kernel GP, optionally reject non-SRM generic boots, locate the HWRPB console callback routine block, shift Linux arguments to the VMS calling convention, extract callback code and argument count from wrapper data, and jump to the SRM dispatch procedure. Non-SRM builds return `-1` immediately.

## State and Persistence Behavior
State is read from HWRPB/CRB fields, `alpha_using_srm`, and callback initialization flags. SRM callbacks may mutate firmware environment variables or console state; this wrapper itself stores only weak default data.

## Dependencies
Depends on `asm/console.h` callback codes, `hwrpb`, Alpha GP/procedure descriptor conventions, SRM firmware, and generic-kernel `alpha_using_srm` detection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Argument shifting and VMS descriptor use are ABI-critical. Calling SRM on non-SRM firmware must return safely. Environment-setting callbacks are persistent firmware operations, so wrong codes or counts can corrupt SRM variables.

## Test Signals
Build SRM and generic Alpha configs, call getenv/setenv/save-env paths on SRM hardware, verify non-SRM stubs return `-1`, and test early console callbacks before and after callback initialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/callback_srm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/checksum.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/checksum.c

## Purpose
Alpha-optimized IPv4/TCP/UDP checksum helpers using 64-bit accumulation and architecture byte extraction. The source was read as part of `subset-b-000628` and contains 186 lines.

## Important APIs, Types, and Functions
Exports `csum_tcpudp_magic`, `csum_tcpudp_nofold`, `ip_fast_csum`, `csum_partial`, and `ip_compute_csum`; internal helpers are `from64to16` and `do_csum`.

## Control Flow
Pseudo-header helpers add source/destination addresses, length, protocol, and previous checksum, then fold or leave a 32-bit nofold value. `do_csum` handles odd starts, aligns through 16/32/64-bit chunks, accumulates carry, folds to 16 bits, and byte-swaps for odd starts. Public helpers complement or add prior partial sums as required by the network stack.

## State and Persistence Behavior
No persistent state. Functions read packet/header memory and return checksum values.

## Dependencies
Depends on Linux checksum types, network stack checksum ABI, Alpha endian behavior, and exported symbol consumers in networking and modules.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Odd alignment and carry folding are subtle; incorrect folding causes silent packet drops. `csum_partial` assumes even lengths except final fragments. Type casts between forced checksum types must preserve network byte order.

## Test Signals
Run network checksum selftests, compare against generic checksum implementation for random aligned/unaligned buffers and odd lengths, test TCP/UDP IPv4 traffic, and build modules that import exported symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/clear_page.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/clear_page.S

## Purpose
Generic Alpha assembly implementation of `clear_page`, zeroing a full kernel page. The source was read as part of `subset-b-000628` and contains 41 lines.

## Important APIs, Types, and Functions
Exports global `clear_page`.

## Control Flow
The routine loops 128 times, storing eight zero quadwords per iteration for 64 bytes, advancing the destination pointer until 8192 bytes are cleared, then returns.

## State and Persistence Behavior
Mutates exactly the destination page memory supplied in `$16`; keeps only register loop state.

## Dependencies
Depends on Alpha calling convention, kernel page size used by Alpha, `EXPORT_SYMBOL`, and callers in page allocator/MM paths.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Assumes page size matches 128 * 64 bytes. Destination must be valid kernel memory and suitably accessible. Any loop count error corrupts adjacent pages or leaves stale data.

## Test Signals
Build non-EV6 Alpha config, allocate pages and verify all bytes zero, run page allocator/MM tests, and inspect symbol export when modules call `clear_page`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/clear_user.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/clear_user.S

## Purpose
Generic Alpha `__clear_user` implementation that zeroes userspace memory while returning the number of bytes not cleared on fault. The source was read as part of `subset-b-000628` and contains 102 lines.

## Important APIs, Types, and Functions
Exports `__clear_user`; defines `EX` exception-table macro and local loop/tail/exception labels.

## Control Flow
The entry computes destination misalignment, handles a partial head with masked unaligned stores, clears aligned quadwords in groups, writes a masked tail, and updates `$0` only after successful stores. Exception-table entries branch to the return path with `$0` containing bytes left.

## State and Persistence Behavior
Mutates user memory and returns residual byte count in `$0`. Persistent state is exception-table metadata emitted into `__ex_table`.

## Dependencies
Depends on Alpha unaligned load/store instructions, exception-table fixups, uaccess ABI, and exported user-copy helpers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Residual count must be exact for uaccess callers. Head/tail masking must not zero bytes outside the requested range. Exception annotations must cover every faulting user access.

## Test Signals
Run usercopy tests with aligned, unaligned, zero-length, short, and page-faulting ranges; verify return counts and surrounding bytes; build generic Alpha library path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/clear_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/copy_page.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/copy_page.S

## Purpose
Generic Alpha assembly implementation of `copy_page`, copying one complete kernel page. The source was read as part of `subset-b-000628` and contains 51 lines.

## Important APIs, Types, and Functions
Exports global `copy_page`.

## Control Flow
Loops 128 times, loading eight source quadwords, storing them to destination, and advancing both pointers by 64 bytes per trip.

## State and Persistence Behavior
Reads one source page and writes one destination page; all other state is register-local.

## Dependencies
Depends on Alpha calling convention, Alpha page size, page allocator/MM callers, and `EXPORT_SYMBOL`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Assumes non-overlapping full-page copies and Alpha page size. Incorrect count or pointer update can corrupt memory. No exception handling is present because this is kernel memory only.

## Test Signals
Run MM/page allocator tests, compare destination with source for randomized pages, verify non-EV6 build selects this implementation, and check exported symbol availability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/copy_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/copy_user.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/copy_user.S

## Purpose
Generic Alpha `__copy_user` implementation for copying between kernel and user address spaces with precise residual count on faults. The source was read as part of `subset-b-000628` and contains 121 lines.

## Important APIs, Types, and Functions
Exports `__copy_user`; defines separate input and output exception macros `EXI` and `EXO`.

## Control Flow
The routine handles destination byte alignment, then chooses aligned-source quadword copies or unaligned rotating loads, finishes with byte/tail copies, and returns `$0` as bytes remaining. Input faults branch to `$exitin`; output faults branch to `$exitout`, preserving the residual count maintained after successful transfers.

## State and Persistence Behavior
Mutates destination memory, reads source memory, returns residual count, and emits exception-table entries.

## Dependencies
Depends on Alpha uaccess exception machinery, unaligned load/store/extract instructions, calling convention, and Linux usercopy API.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Input and output fault paths must preserve caller-visible counts. Masked tail stores must not overwrite adjacent destination bytes. Alignment paths are dense and easy to break with scheduling changes.

## Test Signals
Run hardened/usercopy tests across every source/destination alignment, inject page faults mid-copy, compare residual bytes and memory contents, and build modules that import `__copy_user`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/copy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/csum_ipv6_magic.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/csum_ipv6_magic.S

## Purpose
Generic Alpha assembly implementation of IPv6 pseudo-header checksum folding. The source was read as part of `subset-b-000628` and contains 118 lines.

## Important APIs, Types, and Functions
Exports `csum_ipv6_magic`.

## Control Flow
Loads possibly unaligned 128-bit source and destination IPv6 addresses, byte-swaps/folds length and protocol, adds incoming checksum plus all pseudo-header words with explicit carry tracking, folds the 64-bit sum to 16 bits, complements it, and returns the checksum.

## State and Persistence Behavior
No persistent state; reads address structures and returns a checksum.

## Dependencies
Depends on Alpha unaligned load/extract instructions, Linux checksum ABI, IPv6 stack callers, and module export machinery.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Misalignment handling and byte order are critical. Carry merging errors produce rare packet checksum failures. The function assumes the ABI argument order documented in the file comment.

## Test Signals
Compare against generic IPv6 checksum for random addresses/protocols/lengths/csums, test unaligned `in6_addr` pointers, run IPv6 TCP/UDP traffic, and verify exported symbol resolution.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/csum_ipv6_magic.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/csum_partial_copy.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/csum_partial_copy.c

## Purpose
Alpha implementation of copy-plus-checksum helpers, including user-source fault handling and optimized aligned/unaligned copy/checksum loops. The source was read as part of `subset-b-000628` and contains 363 lines.

## Important APIs, Types, and Functions
Provides `csum_and_copy_from_user`, `csum_partial_copy_nocheck`, exported `csum_partial_copy_nocheck`, and internals `from64to16`, `csum_partial_cfu_aligned`, `csum_partial_cfu_dest_aligned`, `csum_partial_cfu_src_aligned`, `csum_partial_cfu_unaligned`, and `__csum_and_copy`.

## Control Flow
Inline Alpha primitives load/store unaligned quadwords and assemble bytes. The main helper selects an aligned, destination-aligned, source-aligned, or fully unaligned loop, copies data while accumulating checksum and carry, folds the final sum, and uses exception annotations for user reads. The no-check variant passes kernel pointers through the same checksum/copy core.

## State and Persistence Behavior
Mutates destination buffer and returns checksum. User faults affect the returned checksum/error behavior through uaccess exception paths; no global persistent state is kept.

## Dependencies
Depends on Alpha inline assembly, `linux/uaccess.h`, exception-table macros, network checksum ABI, and generic networking callers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The file has many alignment-specific paths; a bug may only appear for one source/destination alignment and odd length. Fault behavior must not leak stale destination data or report a successful checksum after partial copy. Carry folding must match `checksum.c`.

## Test Signals
Differential-test against generic copy+checksum for all alignments and lengths, include page-faulting user buffers, run TCP/UDP receive paths, and verify `csum_partial_copy_nocheck` export for modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/csum_partial_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_current.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_current.S

## Purpose
Profiling/debug `_mcount` hook that traps if the Alpha `current` pointer and stack pointer relationship is inconsistent. The source was read as part of `subset-b-000628` and contains 30 lines.

## Important APIs, Types, and Functions
Defines global `_mcount`; it uses `PAL_bugchk` from `asm/pal.h` as the failure path.

## Control Flow
The hook computes `sp - 0x4000`, checks whether the stack pointer lies within the expected current task stack window relative to register `$8`, and returns through `$28` when valid. If the check fails, it invokes the PAL bugcheck call.

## State and Persistence Behavior
Reads the stack pointer and `$8` current/task register state only; failure enters firmware/kernel bugcheck handling. It does not store persistent data.

## Dependencies
Depends on Alpha profiling instrumentation naming `_mcount`, the convention that `$8` tracks current task state, stack-size assumptions, and PAL `PAL_bugchk`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The hard-coded `0x4000` stack window must match the configured Alpha stack layout. If profiling invokes `_mcount` before registers are established, this can false-trigger a PAL bugcheck.

## Test Signals
Build a debug/profiling Alpha configuration that selects this object, boot with function profiling active, confirm normal calls return without PAL bugcheck, and deliberately inspect stack/current invariants under a debugger.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_current.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackcheck.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackcheck.S

## Purpose
Debug `_mcount` hook that detects Alpha kernel stack overflow and forces an oops when the stack pointer is outside the task stack. The source was read as part of `subset-b-000628` and contains 28 lines.

## Important APIs, Types, and Functions
Defines global `_mcount` and uses `TASK_SIZE` from `asm/asm-offsets.h`.

## Control Flow
The hook computes the end of the current task stack from `$8 + TASK_SIZE`, compares it with `$30` stack pointer, returns normally when within bounds, and otherwise stores through address `-8($31)` in a tight loop to force a fault.

## State and Persistence Behavior
Reads current task and stack pointer registers. On failure it intentionally causes a fault; it does not maintain global state.

## Dependencies
Depends on Alpha `_mcount` instrumentation, task stack layout, `TASK_SIZE`, and the oops path triggered by an invalid store.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
A wrong `TASK_SIZE` or unexpected stack context can either miss real overflow or crash a valid path. The failure path is intentionally destructive.

## Test Signals
Build with stack-check debugging, boot a profiling/debug kernel, run deep-call and interrupt workloads, and verify overflow injection reaches the expected oops path while normal calls return.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackcheck.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackkill.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackkill.S

## Purpose
Debug `_mcount` hook that poisons unused Alpha kernel stack space with `0xdeadbeefdeadbeef` to expose uninitialized stack-variable use. The source was read as part of `subset-b-000628` and contains 36 lines.

## Important APIs, Types, and Functions
Defines global `_mcount`; uses `STACK_SIZE` and `TASK_SIZE` from `asm/asm-offsets.h`.

## Control Flow
The hook builds the 64-bit poison value, aligns from the current stack region toward the active stack pointer, writes the poison pattern in 8-byte steps up to `$30`, and returns through `$28`.

## State and Persistence Behavior
Mutates currently unused stack memory below the active frame. It creates diagnostic stack contents but no persistent global state.

## Dependencies
Depends on Alpha `_mcount` instrumentation, task stack layout constants, and callers tolerating stack poisoning during debug builds.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Wrong stack bounds can corrupt live frames or miss unused stack space. Because it runs from `_mcount`, overhead is high and it must stay confined to debug configurations.

## Test Signals
Build the stack-kill debug configuration, verify stack gaps contain the poison pattern after instrumented calls, run workloads that previously used uninitialized locals, and confirm production configs do not select this object.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackkill.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/divide.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/divide.S

## Purpose
Generic Alpha software integer divide/remainder implementation used to build unsigned/signed and long/quad variants through assembler defines. The source was read as part of `subset-b-000628` and contains 199 lines.

## Important APIs, Types, and Functions
Defines generated division symbols through `ufunction` and `sfunction`, exported for the objects built as `__divqu.o`, `__remqu.o`, `__divlu.o`, and `__remlu.o`.

## Control Flow
The assembly source is parameterized by `DIV`, `REM`, and `INTSIZE`. It normalizes operands, performs bitwise quotient/remainder computation for unsigned and signed cases, applies signs for signed operations, and returns either quotient or remainder depending on the object being built.

## State and Persistence Behavior
No persistent state; operates only on input registers and returns arithmetic results.

## Dependencies
Depends on Makefile-provided assembler defines, Alpha calling convention, kernel arithmetic helper references generated by the compiler, and `EXPORT_SYMBOL`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The same source builds four ABI-visible helpers, so define combinations must be exact. Divide-by-zero and signed overflow behavior must match compiler/runtime expectations. Generic code may be slower than EV6-tuned version but must remain correct on all Alpha CPUs.

## Test Signals
Run arithmetic selftests over signed/unsigned 32- and 64-bit values, compare with compiler builtins in a host model, test divide-by-zero handling expected by callers, and build non-EV6 configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/divide.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_page.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_page.S

## Purpose
EV6/Alpha 21264-tuned implementation of `clear_page`. The source was read as part of `subset-b-000628` and contains 56 lines.

## Important APIs, Types, and Functions
Exports `clear_page` when `CONFIG_ALPHA_EV6` selects the `ev6-` prefix.

## Control Flow
Uses EV6 scheduling, alignment, and store ordering to zero a full page, typically with larger unrolled loops and memory-system hints compared with the generic version.

## State and Persistence Behavior
Writes the destination page; no global state is kept.

## Dependencies
Selected by `arch/alpha/lib/Makefile` for EV6 builds, depends on Alpha 21264 instruction scheduling assumptions and MM callers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
EV6-specific scheduling should not be selected for incompatible CPUs. It must preserve exact page size and not rely on user-access exception handling.

## Test Signals
Build `CONFIG_ALPHA_EV6`, verify `clear_page` resolves from this object, run page allocator zeroing tests, and compare performance/correctness against generic `clear_page`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_user.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_user.S

## Purpose
EV6-optimized `__clear_user` that zeroes userspace memory with exception-table recovery. The source was read as part of `subset-b-000628` and contains 213 lines.

## Important APIs, Types, and Functions
Exports `__clear_user` for EV6 builds.

## Control Flow
Handles misaligned head/tail ranges, clears aligned blocks with EV6-friendly scheduling and write hints, and maintains the residual byte count in the return register after successful stores. Faulting accesses use exception-table entries to return bytes left.

## State and Persistence Behavior
Mutates user memory, returns residual count, and contributes exception-table metadata.

## Dependencies
Depends on EV6 scheduling behavior, Alpha uaccess exception macros, usercopy ABI, and Makefile EV6 selection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Optimization increases risk around residual counts and masked stores. Every user memory access must have the right exception fixup. EV6-only code must not be linked for generic targets.

## Test Signals
Run usercopy clear tests on EV6 config for all alignments, page-faulting tails, and zero lengths; compare with generic helper behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_page.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_page.S

## Purpose
EV6-tuned full-page copy implementation. The source was read as part of `subset-b-000628` and contains 205 lines.

## Important APIs, Types, and Functions
Exports `copy_page` when selected by EV6 builds.

## Control Flow
Copies one page with EV6-scheduled load/store groups and likely cache/write hints, advancing source and destination through the entire page.

## State and Persistence Behavior
Reads a source page and writes a destination page only.

## Dependencies
Selected by Alpha lib Makefile for `CONFIG_ALPHA_EV6`, consumed by MM/page-copy paths, and depends on Alpha page-size assumptions.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Optimized unrolling must copy exactly one page and handle expected alignment. Wrong selection for non-EV6 CPUs may hurt correctness/performance.

## Test Signals
Build EV6 config, verify symbol source, run page-copy memory tests with randomized data, and compare against generic implementation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_user.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_user.S

## Purpose
EV6-optimized `__copy_user` with fault recovery and residual count semantics. The source was read as part of `subset-b-000628` and contains 227 lines.

## Important APIs, Types, and Functions
Exports `__copy_user` for EV6 builds.

## Control Flow
Chooses alignment-specific copy loops, uses EV6 scheduling/cache hints for aligned blocks, handles byte heads/tails, and exception-table branches preserve the number of bytes not copied on source or destination faults.

## State and Persistence Behavior
Reads source, writes destination, returns residual byte count, and emits exception-table entries.

## Dependencies
Depends on Alpha uaccess ABI, EV6 instruction scheduling, Makefile EV6 selection, and callers in `copy_to_user`/`copy_from_user` wrappers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Residual count, source fault, and destination fault paths are ABI-visible. Optimized unaligned paths can corrupt neighboring bytes if masks are wrong.

## Test Signals
Run usercopy fault-injection and alignment tests on EV6 config, validate return counts, and stress filesystem/network syscalls that copy user buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-csum_ipv6_magic.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-csum_ipv6_magic.S

## Purpose
EV6/21264-optimized IPv6 pseudo-header checksum routine. The source was read as part of `subset-b-000628` and contains 153 lines.

## Important APIs, Types, and Functions
Exports `csum_ipv6_magic` when EV6 library selection is active.

## Control Flow
Loads source/destination IPv6 addresses, folds length/protocol and incoming checksum, schedules additions/carry handling for EV6 pipelines, folds to a complemented 16-bit result, and returns it.

## State and Persistence Behavior
No persistent state; reads packet metadata and returns checksum.

## Dependencies
Depends on EV6 instruction scheduling, networking checksum ABI, IPv6 stack callers, and Makefile CPU selection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Byte order and carry folding must exactly match the generic checksum. Misaligned address handling remains necessary. CPU-specific implementation must export the same symbol as generic.

## Test Signals
Differential-test against generic `csum_ipv6_magic` for random aligned and unaligned inputs, run IPv6 TCP/UDP traffic, and verify EV6 builds select this object.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-csum_ipv6_magic.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-divide.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-divide.S

## Purpose
EV6-optimized software divide/remainder source used to build Alpha arithmetic helper variants. The source was read as part of `subset-b-000628` and contains 263 lines.

## Important APIs, Types, and Functions
Defines/export symbols via `ufunction` and `sfunction` for `__divqu`, `__remqu`, `__divlu`, and `__remlu` objects selected by the Makefile.

## Control Flow
Like generic `divide.S`, assembler defines choose divide versus remainder and long versus quad size. The EV6 version uses scheduling better suited to 21264 pipelines while preserving signed/unsigned semantics.

## State and Persistence Behavior
No persistent state; input registers produce quotient or remainder outputs.

## Dependencies
Depends on Makefile flags, EV6 build selection, compiler-emitted arithmetic helper references, and Alpha calling convention.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
All generated variants share one source and must remain ABI-compatible with generic helpers. Signed edge cases and divide-by-zero expectations are high risk.

## Test Signals
Run arithmetic differential tests across the four generated objects on EV6 config, include signed min/-1 and zero divisor cases expected by kernel callers, and verify no generic divide symbols are missing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-divide.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memchr.S

## Purpose
EV6-optimized `memchr` implementation for scanning memory for a byte value. The source was read as part of `subset-b-000628` and contains 193 lines.

## Important APIs, Types, and Functions
Defines global `memchr` selected for EV6 builds.

## Control Flow
Handles initial misalignment, replicates the search byte across a word, uses Alpha byte-compare operations to scan quadwords efficiently, and returns the address of the first match or NULL.

## State and Persistence Behavior
Reads the supplied memory range only; no persistent state.

## Dependencies
Depends on EV6 scheduling, Alpha byte comparison instructions, C library ABI expected by kernel code, and Makefile EV6 selection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Must not read beyond fault-safe kernel buffers in contexts where callers expect bounded access. Off-by-one at head/tail boundaries returns wrong match addresses.

## Test Signals
Run string/memory selftests for every alignment, length 0 through multi-cacheline ranges, no-match and first/last-byte matches, and compare with generic C behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memcpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memcpy.S

## Purpose
EV6/21264 optimized `memcpy` implementation with aligned and misaligned copy paths. The source was read as part of `subset-b-000628` and contains 250 lines.

## Important APIs, Types, and Functions
Exports `memcpy` and provides global `__memcpy = memcpy` for compatibility.

## Control Flow
For aligned copies it moves to 64-byte alignment, uses unrolled loops and `wh64` write hints, then handles quadword and byte tails. For misaligned copies it byte-aligns the destination, uses rotating unaligned loads/extracts to assemble aligned stores, and finishes trailing bytes.

## State and Persistence Behavior
Mutates destination memory and reads source memory; returns the destination pointer in the normal C ABI.

## Dependencies
Selected by EV6 Makefile prefix, depends on Alpha 21264 scheduling/write-hint behavior, and is used by broad kernel C code and modules.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
`memcpy` assumes non-overlap; using it for overlapping ranges is a caller bug. Alignment paths are complex and can corrupt tails. `wh64` hints must not target invalid cache lines.

## Test Signals
Run memory copy selftests over all alignments and sizes, compare with generic implementation, check `__memcpy` alias for module compatibility, and stress boot/filesystem/network paths on EV6.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memset.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memset.S

## Purpose
EV6/21264 optimized implementations of byte and 16-bit memory set routines. The source was read as part of `subset-b-000628` and contains 605 lines.

## Important APIs, Types, and Functions
Defines/exports `___memset`, `__constant_c_memset`, `__memset16`, and aliases `memset = ___memset` and `__memset = ___memset`.

## Control Flow
`___memset` materializes an 8-byte repeated byte pattern, handles single-quadword and misaligned heads, writes aligned quads with unrolled `wh64` loops for large ranges, and masks trailing bytes. `__constant_c_memset` preserves a legacy entry body, and `__memset16` replicates 16-bit patterns with a similar scheduled layout.

## State and Persistence Behavior
Writes destination memory and returns the destination pointer; no global state.

## Dependencies
Depends on EV6 scheduling, Alpha unaligned masking instructions, Makefile EV6 selection, and kernel memory helper ABI.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Multiple replicated bodies must be fixed consistently. Head/tail masks can overwrite adjacent bytes. 16-bit pattern replication must preserve endianness. Alias/export names are module ABI.

## Test Signals
Run memset tests for all alignments, byte values, 16-bit patterns, small and large lengths, compare against generic behavior, and verify exported aliases in EV6 builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxcpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxcpy.S

## Purpose
EV6-optimized internal null-terminated string copy primitive used by string functions such as strcpy, stpcpy, and strcat. The source was read as part of `subset-b-000628` and contains 322 lines.

## Important APIs, Types, and Functions
Defines global `__stxcpy` plus internal aligned/unaligned procedure bodies. It follows special linkage: `t9` is return address, `a0` destination, `a1` source, and on return `t12` marks the last byte written while `a0` points at the last word written.

## Control Flow
The routine first checks source/destination co-alignment. The aligned path masks the first destination word if needed, copies full source words while `cmpbge` detects a zero byte, then writes the final partial word without unnecessary destination loads. The unaligned path assembles shifted source words from paired unaligned loads, avoids reading too far past the terminating byte, and handles final partial stores.

## State and Persistence Behavior
Writes the destination string including the terminating NUL and returns internal linkage state to the public wrapper. It has no global state.

## Dependencies
Depends on Alpha string wrapper conventions in adjacent `stxcpy`/`strcpy`/`strcat` code, EV6 scheduling, Alpha byte-compare and zap instructions, and kernel string ABI.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
This is an internal ABI, so public wrappers depend on preserved registers and return values. It must avoid source over-read across invalid pages. Final partial store masks must preserve destination bytes after the NUL when not overwritten.

## Test Signals
Run string-copy tests for all source/destination alignments, page-boundary strings, empty and long strings, and wrappers using `__stxcpy`; compare final pointers and destination contents with generic string helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxcpy.S -->
