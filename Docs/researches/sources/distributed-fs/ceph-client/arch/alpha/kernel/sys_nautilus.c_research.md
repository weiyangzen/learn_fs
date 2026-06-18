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
