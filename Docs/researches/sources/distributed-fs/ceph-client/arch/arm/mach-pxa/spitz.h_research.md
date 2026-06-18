# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.h

Purpose: board constants for the Sharp Spitz/Borzoi/Akita family.

Important APIs/types/functions: defines SCOOP GPIO bases and bit masks, Akita I/O expander base, many PXA GPIO numbers for reset, keys, switches, SD, CF, USB, touchscreen, LCD, charge, battery, and MAX1111 chip select, plus `SPITZ_IRQ_GPIO_*` IRQ translations.

Control flow: no executable flow; board and PM files consume these constants to wire platform devices and callbacks.

State and persistence: constants describe fixed board wiring and initial/suspend SCOOP output states. They become persistent hardware behavior through GPIO and SCOOP register programming.

Dependencies and integration points: included by `spitz.c` and `spitz_pm.c`; depends on PXA GPIO-to-IRQ macros and the legacy Sharp SCOOP expander model.

Risks: wrong polarity or GPIO number maps a driver to the wrong physical signal, with especially high risk around charger, battery cover, card power, and reset lines.

Test signals: hardware pin validation, GPIO IRQ events, card power toggles, charger status, and board-variant checks for Akita versus Spitz/Borzoi expanders.
