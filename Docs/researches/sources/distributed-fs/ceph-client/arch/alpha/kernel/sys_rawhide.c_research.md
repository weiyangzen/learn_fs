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
