# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.h

Purpose: This header declares the shared probe/remove entry points used by SIMATIC IPC CMOS battery backend modules.

Important APIs, types, and functions: `simatic_ipc_batt_probe(struct platform_device *pdev, struct gpiod_lookup_table *table)` registers the shared hwmon battery monitor with backend-specific GPIO lookup data. `simatic_ipc_batt_remove(struct platform_device *pdev, struct gpiod_lookup_table *table)` removes the lookup table.

Control flow: Backend modules include this header and pass their static lookup table to the shared core during platform-driver probe/remove.

State and persistence: The header has no state. It exposes the shared core's singleton behavior to backend modules.

Dependencies and integration points: It depends on declarations for `struct platform_device` and `struct gpiod_lookup_table` being available through including translation units. It is tightly coupled to `simatic-ipc-batt.c`.

Risks and edge cases: The header does not include the type-defining headers itself, relying on include order in users. API users must pass the same table on remove that they passed on probe.

Test signals: Compile each backend independently and with different include-order changes; validate exported symbol availability when built as modules.
