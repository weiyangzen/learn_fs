# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/shared-psy-info.h

Purpose: declaration header for shared x86 Android tablet power-supply helper data exported by `shared-psy-info.c`.

Important APIs/types/functions: forward-declares `struct bq24190_platform_data`, `struct platform_device_info`, and `struct software_node`, then declares shared supplier-name arrays, fuel-gauge software nodes, generic battery nodes and node groups, `bq24190_pdata`, `bq24190_modules`, and `int3496_pdevs`.

Control flow: none; this is a compile-time interface used by board-description C files.

State and persistence: no state beyond external symbol declarations. The declared objects are static boot-time configuration data owned by `shared-psy-info.c`.

Dependencies/integration: included by x86 Android tablet board shards that need battery, charger, or USB-ID properties. It intentionally avoids pulling in heavy headers by using forward declarations.

Risks: declarations must stay exactly synchronized with definitions in `shared-psy-info.c`; constness and `__initconst` expectations matter because these symbols are consumed in init-only board tables. Missing declarations lead to duplicated ad hoc nodes in board files or compile failures.

Test signals: compile coverage of all board shards including this header, and successful linking of every declared shared symbol.
