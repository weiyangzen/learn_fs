# sources/distributed-fs/ceph-client/arch/sparc/kernel/pcic.c

## Purpose
MicroSPARC-IIep PCIC PCI controller support for 32-bit SPARC systems. Handles early controller probing, config access, hardcoded interrupt routing, bus fixups, timer setup, NMI recovery for speculative config faults, and a PCIC IRQ chip.

## Important APIs, Types, and Functions
`pcic_ca2irq` / `pcic_sn2list` encode system-name interrupt maps. `pcic_probe()` maps PROM register/config/IO windows, patches the NMI trap, selects routing, and marks PCIC present. `pcic_read_config()` / `pcic_write_config()` implement bus-0 config ops. `pcic_init()` disables IOTLB translation, expands PCI memory mapping, and scans. `pcibios_fixup_bus()` attaches cookies, remaps low I/O BARs, and fills IRQs. `pci_time_init()` configures the PCIC timer. `pcic_nmi()` handles speculative PIO traps.

## Control Flow
PCIC probes before normal PCI init. Later `pcic_init()` scans bus 0 and fixups devices. Config reads disable local IRQs, write a config command, perform speculative data reads, and return all ones if the NMI trap records a fault. Timer init binds the counter IRQ to the generic timer interrupt.

## State and Persistence
Static runtime state includes `pcic0_up`, `pcic0`, `pcic_regs`, speculative trap flags, and timer dummy storage. Device fixups allocate cookies. Hardware state includes DVMA control, interrupt-select/mask registers, and timer registers. No persistence.

## Dependencies and Integration Points
Uses PROM APIs, SPARC timer/IRQ configuration, Swift cache flush, PCI core, OF node conversion, and trap table symbols. Integrates through `pcic_ops` and `sparc_config` hooks.

## Risks and Test Signals
Interrupt routing is hardcoded and unknown systems cannot route. Only bus 0 is supported. Low I/O BAR remapping is fragile. Fatal paths halt or spin forever. Test via PCIC boot detection, known routing map, bus scan, IRQ assignment, timer operation, and absent-device config reads returning all ones.
