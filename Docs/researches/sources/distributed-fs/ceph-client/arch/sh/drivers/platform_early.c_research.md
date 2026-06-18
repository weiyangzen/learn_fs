# sources/distributed-fs/ceph-client/arch/sh/drivers/platform_early.c



Source read size: 336 lines, 8899 bytes.



Purpose: SH-specific early platform driver/device framework used before the normal platform bus and full driver core are available.

Important APIs/types/functions: `sh_early_platform_driver_register()`, `sh_early_platform_add_devices()`, `sh_early_platform_driver_register_all()`, `sh_early_platform_driver_probe()`, `early_platform_cleanup()`, matching helpers, and early PM initialization.

Control flow: early drivers are registered into an initdata list, command-line parameters can prioritize and select requested IDs and copy option buffers, devices are stored through their `devres_head` list node, probe iterates requested IDs first then numeric IDs, creates `init_name` when possible, calls probe directly, and cleanup restores device list heads.

State and persistence: init-only global lists hold early drivers/devices; requested IDs and option buffers persist through early probing; cleanup erases temporary list membership.

Dependencies and integration points: integrates early console/clock/platform devices with kernel `early_param()` parsing, platform-driver ID matching, PM runtime fields, and later normal driver core handoff.

Risks and test signals: reusing `devres_head` as a list node is fragile; requested-id parsing errors can suppress probing; `init_name` allocation depends on slab availability. Test early console selection, duplicate command-line options, user-only probing, multiple IDs, and cleanup before normal platform registration.
