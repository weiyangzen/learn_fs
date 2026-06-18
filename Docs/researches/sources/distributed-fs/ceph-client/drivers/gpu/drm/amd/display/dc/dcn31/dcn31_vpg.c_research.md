# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.c

Purpose: Implements DCN31 VPG construction and memory low-power hooks while reusing the DCN30 generic packet writer.

Important APIs/types/functions: `vpg31_construct()` initializes `struct dcn31_vpg`. `vpg31_powerdown()` and `vpg31_poweron()` program `VPG_MEM_PWR`. The function table exposes `.update_generic_info_packet = vpg3_update_generic_info_packet`, `.vpg_poweron`, and `.vpg_powerdown`.

Control flow: Powerdown returns unless `debug.enable_mem_low_power.bits.vpg` is enabled, then clears light-sleep disable and forces light sleep. Poweron reads `VPG_GSP_MEM_PWR_STATE`; if VPG low power is disabled and state is already `0`, it returns, otherwise it disables light sleep and clears force.

State/persistence: Software state is context, instance, function table, and register metadata. Hardware state is inherited generic packet memory/update state plus VPG memory power bits.

Dependencies/integration: Includes `dcn30_vpg.h` for packet programming and `dc/dc.h` for debug low-power flags. Used by DCN31 resource creation.

Risks: The poweron condition has a subtle debug/state dependency; incorrect `VPG_GSP_MEM_PWR_STATE` interpretation could skip wake-up. Packet behavior inherits DCN30's fixed retry and out-of-range-index characteristics.

Test signals: Test low-power disabled/enabled paths, power-state read behavior, and that DCN31 still writes generic packets through `vpg3_update_generic_info_packet()`.
