<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c

Purpose: This file implements Sega Dreamcast Holly/System ASIC hardware event interrupt masking, acknowledgment, demultiplexing, and virtual IRQ setup.

Important APIs/types/functions: It defines ESR/EMR register bases, `LEVEL` and `EVENT_BIT` macros, IRQ-chip callbacks `disable_systemasic_irq`, `enable_systemasic_irq`, `mask_ack_systemasic_irq`, exported `systemasic_int`, demux function `systemasic_irq_demux`, and initializer `systemasic_irq_init`.

Control flow: System ASIC events are grouped into three 32-bit status/mask register sets corresponding to SH IRQ levels 13, 11, and 9. Demux maps the processor IRQ to a group, masks status with enabled bits, scans for the first set event bit, and returns the virtual event IRQ. IRQ chip callbacks update EMR bits and acknowledge by writing the event bit to ESR. Init allocates descriptors for the hardware event range and assigns the chip/level handler.

State and persistence: Hardware EMR/ESR state persists in the ASIC. Kernel IRQ descriptors persist for the hardware event range.

Dependencies and integration points: It depends on Dreamcast `mach/sysasic.h` event ranges, raw I/O accessors, generic IRQ descriptor APIs, and the Dreamcast machine vector's IRQ demux/init callbacks.

Risks and test signals: Event-to-IRQ mapping must match the ASIC register grouping. Acknowledgment must write the correct ESR bit or events will retrigger/latch. Tests include Maple/peripheral interrupts, masking/unmasking behavior, spurious IRQ handling, and descriptor allocation failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/irq.c -->
