<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h

## Purpose
Defines SH architecture declarations and macros for `pci` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_PCI_H`, `pcibios_assign_all_busses()`, `HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, `PCI_DISABLE_MWI`, `pci_domain_nr(bus)`. Structures include `pci_channel`, `pci_bus`, `pci_ops`, `resource`, `timer_list`. Functions or extern declarations include `pcibios_map_platform_irq`, `pci_config_lock`, `register_pci_controller`, `pcibios_report_status`, `early_read_config_byte`, `early_read_config_word`, `early_read_config_dword`, `early_write_config_byte`, `early_write_config_word`, `early_write_config_dword`, `pcibios_enable_timers`, `pcibios_handle_status_errors`, `pci_is_66mhz_capable`, `PCIBIOS_MIN_MEM`.

## Control Flow
Runtime flow is a thin accessor path around memory-mapped hardware: drivers call the macros or inline helpers, the header maps port/MMIO addresses, applies endian conversion or barriers where required, and leaves actual device state in hardware registers.

## State And Persistence
The header stores no durable state. Reads and writes mutate device registers, I/O port windows, or cached/uncached memory aliases; ordering depends on the barriers and uncached transitions encoded by the accessors.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_PCI`. Integration points are Linux driver I/O APIs, machine vectors, PCI/ISA port mapping, platform devices, and board-specific register maps.

## Risks And Edge Cases
Risks include missing barriers, accidental cached access to device memory, incorrect port-base or endian conversion, unimplemented no-I/O-port stubs reaching drivers, and register-map drift from hardware manuals.

## Test Signals
Useful signals are driver probe tests, PCI/ISA I/O enumeration, MMIO ordering tests, DMA transfer tests, endian/sparse checks, and board-level peripheral smoke tests.

Source read size: 91 lines, 2844 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/pci.h -->
