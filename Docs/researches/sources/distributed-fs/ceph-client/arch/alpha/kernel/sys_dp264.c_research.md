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
