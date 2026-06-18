# sources/distributed-fs/ceph-client/drivers/parisc/gsc.h

## Purpose
This private header defines the shared register offsets, constants, data structures, and function prototypes used by PA-RISC GSC ASIC drivers.

## Important APIs, Types, And Functions
Register offsets are `OFFSET_IRR`, `OFFSET_IMR`, `OFFSET_IPR`, `OFFSET_ICR`, and `OFFSET_IAR`. `GSC_EIM_WIDTH` defines the transaction interrupt width. `struct gsc_irq` stores transaction address/data and Linux IRQ number. `struct gsc_asic` stores parent device, HPA, chip identity, EIM, allocated IRQ tuple, and a 32-line IRQ map. The header declares `gsc_common_setup()`, `gsc_alloc_irq()`, `gsc_claim_irq()`, `gsc_assign_irq()`, `gsc_find_local_irq()`, `gsc_fixup_irqs()`, `gsc_asic_assign_irq()`, and `gsc_asic_intr()`.

## Control Flow
This file has no executable control flow. It establishes the contract followed by `gsc.c` and chip drivers such as `lasi.c`: a chip driver fills `struct gsc_asic`, allocates a parent transaction IRQ, registers `gsc_asic_intr()`, initializes common state, and assigns local IRQs to child `parisc_device` nodes.

## State And Persistence
The structures declared here describe persistent per-ASIC interrupt state stored by chip drivers. The header itself owns no storage.

## Dependencies And Integration Points
It includes Linux interrupt declarations and PA-RISC hardware/device definitions. It is intentionally local to `drivers/parisc` and aligns with the GSC register model used by LASI/ASP/Wax-style bridge drivers.

## Risks
The fixed 32-entry `global_irq` array encodes an architectural assumption shared by all users. Any chip with a wider local interrupt register would need a new contract. The header has no include guard in the shown file, so repeated inclusion depends on current include patterns not causing duplicate declarations with side effects.

## Test Signals
Compile coverage is the main signal for this header. Runtime signals come from users: valid local IRQ assignment, correct register offsets, and stable ABI between `gsc.c` and chip-specific drivers.
