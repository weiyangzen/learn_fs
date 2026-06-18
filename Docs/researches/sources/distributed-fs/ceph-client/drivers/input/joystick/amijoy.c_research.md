# sources/distributed-fs/ceph-client/drivers/input/joystick/amijoy.c

Purpose: Linux/m68k Amiga joystick driver for up to two classic Amiga joystick ports. It samples Amiga custom chip/CIA registers on vertical blank interrupts and reports a two-axis digital stick plus trigger button per configured port.

Important APIs/types/functions: Module parameter `map` controls which of the two ports are active. Global `amijoy_dev[2]` holds input devices, `amijoy_used` counts open users, and `amijoy_mutex` serializes IRQ installation. `amijoy_interrupt()` reads `amiga_custom.joy0dat`/`joy1dat` and `ciaa.pra`, converts bit pairs into -1/0/1 ABS_X and ABS_Y, and reports `BTN_TRIGGER`. `amijoy_open()` requests `IRQ_AMIGA_VERTB`; `amijoy_close()` frees it on last user.

Control flow: Module init rejects non-Amiga machines, allocates one input device per enabled port, reserves the custom register memory region, sets capabilities, and registers inputs. Opening any device installs the shared VBL interrupt if needed. Interrupts report current state for enabled ports. Module exit unregisters inputs and releases regions.

State and persistence: Only global module state is kept: enabled map, open count, input device pointers, and static phys strings. No persistent state exists.

Dependencies and integration points: Tied to Amiga architecture headers and hardware registers, `IRQ_AMIGA_VERTB`, input core, and memory region reservation around Denise joystick registers.

Risks: Hardware-specific bit conversions are difficult to test off m68k Amiga. The keybit setup references `BTN_LEFT`/mouse button word while reporting `BTN_TRIGGER`, so capability consistency should be checked in this tree. Shared IRQ lifetime depends on balanced open/close counts.

Test signals: Boot on Amiga or emulator with `MACH_IS_AMIGA`; verify two-port `map` variations; open two devices concurrently and ensure a single IRQ request/free cycle; validate ABS_X/ABS_Y direction and trigger events against real register changes.
