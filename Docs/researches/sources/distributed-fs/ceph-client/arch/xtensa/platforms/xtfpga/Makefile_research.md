# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/Makefile

Purpose: Builds XTENSA XTFPGA/XTAVNET board support and optional LCD support.

Important APIs, types, and functions: `obj-y += setup.o` and `obj-$(CONFIG_XTFPGA_LCD) += lcd.o`.

Control flow: Kbuild always includes platform setup for XTFPGA and conditionally includes LCD driver support.

State and persistence: No runtime state in the Makefile; controls board object inclusion.

Dependencies and integration: XTFPGA platform Kconfig, hardware/serial/LCD headers, setup and optional LCD implementation.

Risks: Optional LCD declarations in `lcd.h` must match this object selection; missing setup object breaks platform hooks.

Test signals: XTFPGA builds with and without `CONFIG_XTFPGA_LCD`, link symbol resolution for LCD APIs, and board boot.
