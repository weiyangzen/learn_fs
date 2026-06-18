# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/Makefile

Purpose: Builds XT2000 emulation board platform setup.

Important APIs, types, and functions: `obj-y = setup.o`.

Control flow: When XT2000 platform is selected, kbuild links `setup.o` to provide `platform_setup()` and device registration for the board.

State and persistence: No runtime state in the Makefile; it controls inclusion of board support.

Dependencies and integration: XT2000 Kconfig selection, platform headers for hardware/serial, and generic Xtensa platform hooks.

Risks: Missing `setup.o` would leave board devices and power handlers unavailable.

Test signals: XT2000 platform build and boot with serial/SONIC device registration.
