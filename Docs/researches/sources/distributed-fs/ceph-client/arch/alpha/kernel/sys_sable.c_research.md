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
