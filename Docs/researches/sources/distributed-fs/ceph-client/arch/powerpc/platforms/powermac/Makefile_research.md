# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Makefile

Purpose: PowerMac object list and special compiler flags for BootX early boot code.

Important APIs and control flow: `bootx_init.o` is built position-independent, without stack protector, without KASAN instrumentation, and with ftrace removed because it runs before normal runtime support. Core PowerMac objects include PIC, setup, time, feature, PCI, sleep, I2C, cache, platform functions, and udbg. Optional objects add backlight, NVRAM, BootX on PPC32, and SMP.

State, dependencies, and risks: state is build-time object inclusion and per-object instrumentation policy. Dependencies include Kconfig symbols and early-boot constraints. Risks are accidentally instrumenting `bootx_init.o`, NVRAM tristate coercion behavior, and missing optional objects under platform configs. Test signals are PowerMac 32/64 links, BootX boot path without instrumentation faults, and optional backlight/NVRAM/SMP symbols resolving.
