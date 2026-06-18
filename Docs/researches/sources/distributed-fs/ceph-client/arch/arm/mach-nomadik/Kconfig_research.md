<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig

Purpose: Kconfig for ST-Ericsson Nomadik STn8815 platform support. It selects the ARM926T, VIC, MTU timer, GPIO, syscon, pinctrl, and board-specific I2C support for the NHK board.

Important APIs/types/functions: Symbols include `ARCH_NOMADIK`, `MACH_NOMADIK_8815NHK`, and `NOMADIK_8815`.

Control flow, state, and persistence: It has no runtime state; it constrains build-time inclusion and driver availability.

Dependencies and integration points: Symbols include `ARCH_NOMADIK`, `MACH_NOMADIK_8815NHK`, and `NOMADIK_8815`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks include legacy board dependency on non-DT pieces and broad selected dependencies. Test multi-v5 builds and NHK board config.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 32 lines, 648 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig -->
