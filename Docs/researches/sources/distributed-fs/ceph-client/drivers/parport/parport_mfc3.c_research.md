# sources/distributed-fs/ceph-client/drivers/parport/parport_mfc3.c

## Purpose
`parport_mfc3.c` is the low-level parport driver for Amiga Multiface III Zorro expansion cards. It maps the card's MC6821 PIA registers to parport operations and supports up to five cards sharing the Amiga ports interrupt.

## Important APIs, Types, and Functions
The driver uses `MAX_MFC`, global `this_port[]`, shared `use_cnt`, and `pp_mfc3_ops`. Data/control/status functions translate between PC parport bits and MFC3 PIA pins. `mfc3_interrupt()` scans registered cards for PIA interrupt status and calls `parport_generic_irq()`. `parport_mfc3_init()` discovers Zorro devices, initializes PIA data/status directions, registers ports, requests shared IRQ on first user, and announces each port. Exit unregisters all ports and releases resources.

## Control Flow
Init first requires `MACH_IS_AMIGA`, then loops over `ZORRO_PROD_BSC_MULTIFACE_III` devices. For each card it requests the PIA memory region at `resource.start + PIABASE`, maps it with `ZTWO_VADDR`, programs PIA control/data direction, pulses printer reset, registers a parport, requests the shared IRQ once, stores the port, sets `p->dev` and private physical base, then announces. Removal reverses this per slot and frees the IRQ when the last user exits.

## State and Persistence
State is the global port array, shared IRQ use count, dummy volatile reads used to clear interrupt bits, and PIA register contents. Per-port `private_data` stores the physical PIA base for release. Parport state callbacks save and restore PIA data/direction/status fields in `u.amiga`.

## Dependencies and Integration Points
The driver depends on `multiface.h`, Amiga/Zorro APIs, MC6821 PIA definitions, Amiga IRQs, parport core, and generic IEEE 1284 operations. It integrates with Zorro device discovery rather than platform-device probing.

## Risks
The interrupt handler scans all registered ports and always returns `IRQ_HANDLED`, which can mask unexpected shared IRQ causes. State save/restore manipulates PIA DDR visibility and must restore control-register mode correctly. Probe failure after shared IRQ request or partial card setup relies on local labels and loop continuation; multi-card cleanup needs `use_cnt` consistency. Generic advanced IEEE 1284 ops may exceed what the card/peripheral timing supports.

## Test Signals
Tests should cover discovery of zero, one, and multiple cards; memory-region conflict handling; shared IRQ request/free only on first/last port; data and status bit translation; interrupt clearing via PIA reads; parport announce/remove; and save/restore of PIA direction registers.
