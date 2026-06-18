<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c

Purpose: MVEBU system-controller support for restart, SoC identification, Armada 375 SMP workaround, and CPU boot address storage. It maps the system-controller node early and exposes helpers used by SMP and PM.

Important APIs/types/functions: Important APIs are `mvebu_restart`, `mvebu_system_controller_get_soc_id`, `mvebu_system_controller_set_cpu_boot_addr`, and `mvebu_system_controller_init`.

Control flow, state, and persistence: State is the mapped controller base, selected register offsets, and compatible-driven feature bits. Restart writes reset-request bits; SoC ID reads dev/rev fields; boot address writes the physical startup address to a shared register.

Dependencies and integration points: Important APIs are `mvebu_restart`, `mvebu_system_controller_get_soc_id`, `mvebu_system_controller_set_cpu_boot_addr`, and `mvebu_system_controller_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT compatible strings for Armada controllers, `__pa_symbol`, reboot framework, and optional BootROM workaround setup. Risks are incompatible register offset tables, early mapping failure, and SMP boot address writes before init. Test reboot, sysfs SoC ID, Armada 375 secondary boot, and missing-controller fallback.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 177 lines, 4683 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c -->
