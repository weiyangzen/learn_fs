# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Makefile

Purpose: Build rules for the I-Force core and transport drivers.

Important APIs/types/functions: `obj-$(CONFIG_JOYSTICK_IFORCE) += iforce.o` builds the core composite object. `iforce-y := iforce-ff.o iforce-main.o iforce-packets.o` defines its constituent source files. `obj-$(CONFIG_JOYSTICK_IFORCE_232) += iforce-serio.o` and `obj-$(CONFIG_JOYSTICK_IFORCE_USB) += iforce-usb.o` build transport modules.

Control flow: Kbuild composes `iforce.o` from force-feedback construction, core input initialization, and packet handling. USB and serio transports are separate module objects that include the shared header and call exported core functions.

State and persistence: No runtime state; build-only artifact.

Dependencies and integration points: Mirrors Kconfig symbols and exports from `iforce-main.c`, `iforce-packets.c`, and `iforce.h`.

Risks: Transport modules are separate from the core, so symbol export/import and module load ordering matter. Kconfig allows core without transports.

Test signals: Build all three symbols as built-in and modules; ensure `iforce.o` contains all core objects; modpost should resolve exported `iforce_init_device`, `iforce_send_packet`, and `iforce_process_packet`.
