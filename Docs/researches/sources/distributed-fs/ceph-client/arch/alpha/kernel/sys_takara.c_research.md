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
