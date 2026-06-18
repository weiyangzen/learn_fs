# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/riscpc.c

Purpose: main Acorn RiscPC machine descriptor and board initialization.

Important APIs/types/functions: defines I/O mappings, platform devices/resources for onboard peripherals, machine init, fixup/reserve behavior, and the `MACHINE_START` descriptor.

Control flow: early boot maps fixed I/O windows, initializes IRQ/timer through platform hooks, registers devices such as IDE/keyboard/mouse/display support, and uses ATAGS-era machine setup rather than DT.

State and persistence: installs static platform resources, memory mappings, and machine callbacks. No persistent storage.

Dependencies and integration points: integrates IOMD, ecard, DMA, Acorn framebuffer, legacy timers, and ATAGS boot.

Risks: highly legacy static setup; resource addresses must match hardware and the compiler/toolchain restrictions in Kconfig. Missing platform device registration can strand onboard hardware.

Test signals: complete RiscPC boot, onboard IDE/serial/keyboard/mouse/display, expansion cards, timer tick, and machine restart/power behavior.
