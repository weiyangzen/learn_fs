# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_int.h

Purpose: defines SB1250 interrupt source numbers, per-source masks, interrupt mapper values, LDT interrupt set fields, and interrupt vector format.

Important APIs/types/functions: important constants include `K_INT_SOURCES`, source IDs for watchdogs, timers, SMBus, UARTs, serial, PCMCIA, address trap, performance counter, ECC, IO bus, MACs, data mover channels, mailboxes, GPIO 0-15, and LDT classes. `M_INT_*` masks mirror those source IDs. Mapper fields encode interrupt destination and delivery mode, while vector fields provide interrupt number and pending bits.

Control flow: interrupt setup code maps hardware sources to CPU interrupt lines, masks/unmasks sources, reads source status, and decodes vectors. Drivers use the numeric constants to request or route platform interrupts.

State and persistence: the header has no state, but its masks operate on interrupt mapper registers that persist until changed. Source status and vector fields reflect hardware pending state.

Dependencies and integration: depends on `sb1250_defs.h` and feature gates for pass2/112x additions such as cycle counter interrupts and LDT error/eject sources. It integrates with `sb1250.h` IRQ counts, `sb1250_regs.h` IMR addresses, board GPIO interrupt assignments, and device drivers.

Risks and test signals: source-number drift is high impact because it silently routes handlers to the wrong hardware. Feature-gated sources must align with the selected SoC revision. Test signals include build coverage for old/new feature masks, interrupt-controller initialization checks, per-source mask bit validation, GPIO interrupt tests, timer/watchdog interrupt tests, and LDT interrupt injection where supported.
