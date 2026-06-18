## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fourport.c

Purpose: legacy static platform-device registration for AST Fourport-compatible 8250 boards. It publishes two groups of four fixed I/O ports to the generic serial8250 platform layer.

Important APIs, types, and functions: `SERIAL8250_FOURPORT()` wraps `SERIAL8250_PORT_FLAGS()` with `UPF_FOURPORT`. `fourport_data[]` lists ports at `0x1a0`..`0x1b8` on IRQ 9 and `0x2a0`..`0x2b8` on IRQ 5. `fourport_device` is named `serial8250` with ID `PLAT8250_DEV_FOURPORT`. `fourport_init()` registers it at module init.

Control flow: module init registers one platform device; generic 8250 code parses the static port list and handles hardware probing, tty registration, and interrupts.

State and persistence: static table only. There is no per-device allocation or remove callback in this file. All runtime state lives in serial8250 once the platform device is registered.

Dependencies and integration points: integrates with `serial8250` platform probing through `platform_data`; `UPF_FOURPORT` tells the common code to use fourport interrupt semantics.

Risks: fixed ISA-style resources can conflict or create false-positive ports if loaded on machines without the board. Test signals: verify all eight fixed entries are exposed only when intended, shared interrupt behavior works for each group, and `UPF_FOURPORT` produces correct interrupt acknowledgment under RX/TX load.
