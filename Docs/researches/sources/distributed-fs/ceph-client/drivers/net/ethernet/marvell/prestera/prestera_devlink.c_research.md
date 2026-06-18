# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.c

Purpose: Implements Prestera devlink integration: switch allocation/registration, physical devlink ports, firmware version reporting, devlink traps/groups, packet trap reporting, and devlink drop counters.

Important APIs/types/functions: `prestera_devlink_alloc/free/register/unregister()`, `prestera_devlink_port_register/unregister()`, `prestera_devlink_traps_register/unregister()`, `prestera_devlink_trap_report()`. Internal `struct prestera_trap` maps a devlink trap to a firmware CPU code; `struct prestera_trap_item` stores action and devlink trap context; `struct prestera_trap_data` is hung off `sw->trap_data`.

Control flow: switch setup allocates `struct prestera_switch` as devlink private data, registers trap groups, then registers each trap from `prestera_trap_items_arr`. Devlink calls `prestera_trap_init()` to bind trap contexts. RX code reports trapped packets by CPU code through `prestera_devlink_trap_report()`, which looks up the trap item and calls `devlink_trap_report()` with the ingress devlink port. `trap_drop_counter_get` converts the devlink trap back to its CPU code and queries firmware counters via `prestera_hw_cpu_code_counters_get()`.

State and persistence: State is runtime-only: devlink object lifetime, per-port `struct devlink_port`, allocated `sw->trap_data`, trap context pointers, and initial actions. There is no persistent storage. Trap actions cannot be changed because `prestera_trap_action_set()` returns `-EOPNOTSUPP`.

Dependencies/integration: Depends on `net/devlink.h`, Prestera switch/port structures, and `prestera_hw` CPU-code counter commands. Integrated from `prestera_main.c` during switch and port creation, and from RX/TX handling when CPU-tagged packets are reported.

Risks: The trap table must stay synchronized with firmware CPU code assignments and devlink documentation. Unknown CPU codes are silently ignored in trap reporting. Error unwind during registration must mirror partial trap/group registration exactly. Counter support assumes the firmware maps all driver trap CPU codes to requested counter types.

Test signals: Build warnings around devlink API compatibility, `devlink trap show`, per-trap packet reports, `devlink trap stats`, firmware version from `devlink dev info`, port registration visibility, and injection of CPU-trapped packets for representative CPU codes.
