## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Makefile

Purpose: builds the BCM47XX platform support objects.

Important build entries: always includes `irq.o prom.o serial.o setup.o time.o` and `board.o buttons.o leds.o workarounds.o`. This subset covers `irq.o`, `board.o`, and `buttons.o`; the other objects provide the remaining platform boot, console, time, LED, and workaround behavior.

Control flow: none in the Makefile. Object inclusion exposes the platform hooks and init routines expected by BCM47XX boot.

State and persistence: none directly.

Dependencies and integration: uses Kbuild under BCM47XX platform selection. The object list assumes board detection, button and LED registration, bus setup, and workaround init are all part of the platform image.

Risks: no conditional gating is present in this file, so code must internally handle SSB versus BCMA and supported board differences. Removing an object can silently drop platform features.

Test signals: built image should contain IRQ dispatch, PROM/setup/time, serial, board detection, buttons, LEDs, and workaround symbols. Boot should call the appropriate init paths.
