<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c

Purpose: PnP BIOS protocol backend. It discovers the PnP BIOS install structure, initializes BIOS call support, enumerates device nodes, implements dynamic resource get/set/disable, and optionally monitors docking station state.

Important APIs/types/functions: global `pnp_bios_install`, `node_info`, `pnpbios_dont_use_current_config`, and `pnpbios_protocol`. Functions include `pnpbios_probe_system()`, `pnpbios_init()`, `build_devlist()`, `insert_device()`, protocol callbacks `pnpbios_get_resources/set_resources/disable_resources()`, `pnpbios_zero_data_stream()`, boot parser `pnpbios_setup()`, DMI blacklist, and docking thread helpers.

Control flow: init skips disabled/DMI/arch-disabled systems and defers to ACPI PnP when enabled. It scans 0xf0000-0xffff0 for a valid `$PnP` structure with checksum/version, initializes BIOS call descriptors, reads node info, registers protocol, starts proc support, builds device list from dynamic or static nodes, and marks platform devices. Device insertion parses data streams, sets capabilities based on BIOS flags, clears inactive resources, and registers PnP devices. Dynamic get/set allocates a max-node buffer, reads a node, parses or updates resources, and calls BIOS set. Disable zeroes resource stream before BIOS set.

State/persistence: PnP BIOS firmware owns node configuration and possible NVRAM boot state. Software stores node info, device list, active flags, and optional docking thread state. Boot parameter controls whether current config is avoided.

Dependencies/integration: PnP core, low-level BIOS calls, resource parser, proc interface, DMI, ACPI conflict avoidance, kthread/freezer, and usermode helper `/sbin/pnpbios` for dock events.

Risks: legacy firmware may fault; blacklist and `pnpbios=off/no-curr` mitigate. `pnpbios_zero_data_stream()` walks firmware data and logs if no end tag. Dock helper launches an obsolete userspace path. ACPI coexistence disables this backend to avoid duplicate platform devices.

Test signals: valid/invalid install structures, checksum/version rejection, ACPI enabled/disabled interactions, dynamic vs static node enumeration, resource set/disable, DMI blacklist, boot parameters, and docking service status cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c -->
