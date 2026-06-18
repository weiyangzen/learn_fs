# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/Makefile

Purpose: Builds platform support for the Xtensa Instruction Set Simulator.

Important APIs, types, and functions: Always builds `setup.o`; conditionally builds `console.o` for TTY, `network.o` for NET, and `simdisk.o` for simulated block devices.

Control flow: Kbuild includes simulator platform setup unconditionally for ISS and adds optional simulated devices based on kernel features.

State and persistence: No runtime state; controls inclusion of simulator exit/restart, console, network, and block-device support.

Dependencies and integration: ISS platform Kconfig, simulator `simcall` host services, TTY, network, and block subsystems.

Risks: Optional drivers depend on host simcall service availability; enabling devices without simulator support can produce runtime failures even if build succeeds.

Test signals: ISS boot with minimal config, serial console config, `ethX=` tuntap config, and simdisk module/built-in config.
