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
