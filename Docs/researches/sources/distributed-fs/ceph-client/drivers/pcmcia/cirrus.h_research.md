# sources/distributed-fs/ceph-client/drivers/pcmcia/cirrus.h

Purpose: Provides register and bit definitions for Cirrus Logic PD672x/PD6730/PD6832 PCMCIA/CardBus controllers, primarily for Yenta or legacy bridge tuning code.

Important APIs and types: Defines offsets such as `PD67_MISC_CTL_1`, `PD67_EXT_INDEX`, `PD67_TIME_SETUP()`, `PD67_TIME_CMD()`, `PD67_TIME_RECOV()`, and PD6832 extension registers. Bit masks cover voltage detection, speaker/IRQ/media enable, FIFO, suspend, DMA modes, timing scale/multiplier, extension controls, IRQ/power routing, PCI space, and bridge control.

Control flow: No executable logic. Consumers combine these constants with controller config/index register accessors.

State and persistence: The header names hardware registers whose values persist in the controller until reset, suspend/resume restore, or driver reprogramming.

Dependencies and integration points: Integrated by bridge drivers that know `struct yenta_socket` or ExCA register access. It intentionally contains only hardware constants and no Linux object ownership.

Risks: Register definitions encode vendor-specific behavior. A wrong mask or offset can silently corrupt bridge power, timing, or IRQ routing. Licensing header is dual MPL/GPL historical text and should be preserved if copied.

Test signals: Compile the drivers that include it, inspect bridge config dumps before/after tuning, and validate Cirrus-based socket power, timing, DMA, and IRQ behavior.
