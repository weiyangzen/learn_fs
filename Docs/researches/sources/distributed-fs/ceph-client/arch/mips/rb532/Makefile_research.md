# sources/distributed-fs/ceph-client/arch/mips/rb532/Makefile

Purpose: build rules for Mikrotik RB532 board support. It selects the board-specific interrupt, time, setup, PROM, GPIO, and platform-device objects, with an optional early serial object for 8250 console builds.

Important APIs and control flow: `obj-y` always includes `irq.o time.o setup.o prom.o gpio.o devices.o`. `serial.o` is included only under `CONFIG_SERIAL_8250_CONSOLE`.

State, persistence, and integration: it has no runtime state but controls which board hooks satisfy the MIPS architecture entry points. Dependencies include `CONFIG_SERIAL_8250_CONSOLE` and the rc32434 machine headers. Risks are link-time omission of early serial setup if console config changes and tight coupling among objects through globals such as `idt_cpu_freq` and exported latch helpers. Test signals are successful RB532 kernel link and expected object inclusion in build logs.
