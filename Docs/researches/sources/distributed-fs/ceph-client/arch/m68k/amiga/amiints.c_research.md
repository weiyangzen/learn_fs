# sources/distributed-fs/ceph-client/arch/m68k/amiga/amiints.c

Purpose: Amiga custom-chip interrupt fan-out and IRQ chip setup.

Important functions are `amiga_init_IRQ()` and chained handlers `ami_int1`, `ami_int3`, `ami_int4`, and `ami_int5`. The `amiga_irq_chip` enables/disables machine IRQ sources by writing `amiga_custom.intena` based on `IRQ_USER` offset. Chained handlers read `intreqr & intenar`, acknowledge individual custom-chip bits, and call `generic_handle_irq()` for logical Amiga IRQs.

Control flow initializes a range of Amiga IRQs with `m68k_setup_irq_controller()`, installs chained handlers on autovectors 1, 3, 4, and 5, disables PCMCIA interrupts except IDE when Gayle is present, clears pending interrupts, enables the master interrupt bit, and delegates CIA setup to `cia_init_IRQ()` for CIAA/CIAB.

State is hardware interrupt enable/request registers plus IRQ-core chip/handler assignment. No persistent software queue is maintained.

Dependencies include `asm/amigahw.h`, `asm/amigaints.h`, `asm/amipcmcia.h`, `cia.c`, and generic irq APIs. Integration connects Paula/custom-chip hardware to Linux logical IRQs and downstream serial, floppy, audio, blitter, copper, vblank, and disk-sync drivers.

Risks and test signals: incorrect acknowledgement can lose or storm interrupts; IF_RBF is intentionally not acknowledged here because serial handles it. Test with vblank timer users, serial receive, audio IRQ users, floppy, and `/proc/interrupts` counts on Amiga hardware or emulator.
