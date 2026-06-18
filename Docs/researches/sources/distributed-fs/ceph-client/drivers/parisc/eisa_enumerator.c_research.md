# sources/distributed-fs/ceph-client/drivers/parisc/eisa_enumerator.c

## Purpose
This file parses HP PA-RISC EISA EEPROM records, enables detected boards, claims their memory and I/O resources, initializes configured ports, and records IRQ polarity for the EISA PIC setup. It is the platform-specific discovery pass that runs before the Linux EISA core independently enumerates the root bus.

## Important APIs, Types, And Functions
The entry point is `eisa_enumerator()`. EEPROM decoding helpers include `get_8()`, `get_16()`, `get_24()`, `get_32()`, and `print_eisa_id()`. Per-record handlers are `configure_memory()`, `configure_irq()`, `configure_dma()`, `configure_port()`, `configure_port_init()`, `configure_choise()`, `configure_type_string()`, and `configure_function()`. Slot-level orchestration is split between `init_slot()` and `parse_slot_config()`.

## Control Flow
`eisa_enumerator()` copies the entire EEPROM into a static buffer using `gsc_readb()`, reads the EEPROM header, and walks each configured slot. For each slot, `init_slot()` optionally reads the slot ID from the EISA product ID port, verifies it against EEPROM expectations, and enables the board if supported. If the slot has in-range configuration data, `parse_slot_config()` walks function records, skips disabled or free-form functions, and consumes sections in the order implied by flags: type, memory, IRQ, DMA, I/O port, and port initialization. Memory and port sections allocate `struct resource` objects and call `request_resource()` under the EISA HBA parent resources; IRQ sections call `eisa_make_irq_level()` or `eisa_make_irq_edge()`.

## State And Persistence
The enumerator persists resource reservations and hardware side effects. Resource objects allocated for claimed EISA memory/I/O ranges intentionally survive for the lifetime of the booted kernel. Port-init records perform immediate `inb/outb/inw/outw/inl/outl` operations. IRQ polarity is stored indirectly in `eisa.c` global trigger-state variables before the PIC is initialized.

## Dependencies And Integration Points
It depends on the EEPROM record definitions in `asm/eisa_eeprom.h`, EISA I/O helpers routed through PA-RISC port access, Linux resource trees, and the EISA PIC trigger helpers in `eisa.c`. The returned slot count becomes `eisa_root_device.slots` in `eisa_probe()`.

## Risks
The parser trusts EEPROM lengths heavily and has only coarse length mismatch checks after walking each function. Several record types are incomplete or noted as TODOs: free-form configuration, CRC validation, masked port init details, and memory decode modes beyond the implemented form. Resource allocation failures return immediately but already-claimed earlier resources are not unwound. `configure_port()` computes `end` as base plus size plus one, which should be reviewed against Linux resource inclusive-end convention. Port-init with masks has suspicious operand grouping in some reads and is marked unverified by the original code.

## Test Signals
Good signals include correct EISA ID logging, expected resource reservations, initialized IRQ polarity before `init_eisa_pic()`, and slot count matching EEPROM header. Tests should cover absent cards, ID mismatches, disabled functions, free-form functions, malformed lengths, memory/port claim collisions, and multi-function cards with mixed memory, IRQ, DMA, and port-init records.
