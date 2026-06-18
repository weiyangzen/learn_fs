# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.h

Purpose: central hardware-abstraction contract for ctxfi chip backends.

Important APIs and types: enums `CHIPTYP`, `CTCARDS`, and `ADCSRC`; `struct card_conf`; `struct capabilities`; and `struct hw`, a large function-pointer table for card lifecycle, PLL, ADC selection, optional PM, SRC/SRCIMP/AMIXER/DAIO register programming, timer interrupts, and hardware metadata. Also declares `create_hw_obj`, `destroy_hw_obj`, `get_field`, `set_field`, and IRQ bit masks.

Control flow and integration: generic resource managers program hardware only through `struct hw` callbacks, letting 20K1 and 20K2 backends share ATC/resource-manager logic while differing in register layout.

State and persistence: `struct hw` stores PCI/card pointers, IRQ, I/O/memory bases, chip type, model, and optional IRQ callback data. Hardware register state is volatile and backend-owned.

Risks and test signals: broad callback surface makes backend completeness critical. Tests should instantiate both backends, create every resource manager, exercise SRC/AMIXER/DAIO commits, timer callback, ADC source switches, and PM callbacks where configured.
