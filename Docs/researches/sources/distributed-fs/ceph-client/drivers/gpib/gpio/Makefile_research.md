# sources/distributed-fs/ceph-client/drivers/gpib/gpio/Makefile

Purpose: builds the GPIO bit-banged GPIB adapter when `CONFIG_GPIB_GPIO` is enabled. The single target is `gpib_bitbang.o`.

Important build API: `obj-$(CONFIG_GPIB_GPIO) += gpib_bitbang.o` compiles the Raspberry-Pi-oriented software handshake driver and registers one board interface using `KBUILD_MODNAME` as its name.

Control flow and integration: this module depends on `gpib_common` exports, GPIO descriptor/lookup APIs, IRQ APIs, and GPIB state machine definitions. It has no hardware helper core such as NEC7210; the C file directly implements bus handshakes.

State and persistence: no runtime state in the Makefile. Enabling the config makes the bit-banged board type available to user space.

Dependencies: Kconfig should require GPIB common support, gpiolib, IRQ support for GPIO lines, and the target platform GPIO labels used by the lookup tables.

Risks: building the module is not enough for portability; the C file documents Raspberry Pi limitations and hard-coded pin maps. Missing Kconfig dependencies would produce compile or load-time failures.

Test signals: build with `CONFIG_GPIB_GPIO=m`, load on Raspberry Pi GPIO-capable kernels, validate module parameters `pin_map`, `sn7516x_used`, and `debug`, and verify registration/unregistration.
