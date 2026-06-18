# sources/distributed-fs/ceph-client/tools/lib/thermal/commands.c

Purpose: Implements synchronous generic-netlink thermal command requests for listing zones/cooling devices and reading trips, temperatures, governors, and thresholds, plus threshold mutation commands.

Important APIs/types/functions: Static parsers include `parse_tz_get()`, `parse_cdev_get()`, `parse_tz_get_trip()`, `parse_tz_get_temp()`, `parse_tz_get_gov()`, and `parse_threshold_get()`. Public APIs include `thermal_cmd_get_tz()`, `thermal_cmd_get_cdev()`, `thermal_cmd_get_trip()`, `thermal_cmd_get_governor()`, `thermal_cmd_get_temp()`, threshold get/add/delete/flush, `thermal_cmd_init()`, and `thermal_cmd_exit()`.

Control flow: `thermal_cmd_init()` connects a netlink socket, registers local command metadata, resolves the thermal family, and verifies `nlctrl`. Command APIs build a netlink message in `thermal_genl_auto()`, optionally encode zone/threshold attributes, send it via `nl_send_msg()`, and parse replies in `handle_netlink()` based on command id. Dump replies allocate sentinel-terminated arrays.

State and persistence: Mutates `struct thermal_handler` command socket/callback fields and fills caller-visible `thermal_zone`, `thermal_cdev`, `thermal_trip`, and `thermal_threshold` arrays. Arrays use sentinel `id = -1` or `temperature = INT_MAX` and must be freed by callers.

Dependencies/integration: Depends on libnl generic netlink, Linux thermal generic-netlink UAPI constants, public `thermal.h`, and private `thermal_nl.h` helpers.

Risks: `realloc()` failure overwrites the only pointer, leaking prior entries and returning error. Parsers assume attributes arrive in an order where ID/temp precedes other fields; malformed kernel messages could index `size - 1` before allocation. `thermal_cmd_init()` does not disconnect/unregister resources on later failure paths. Threshold add/delete/flush use the same parser callback metadata although those commands may not return payloads.

Test signals: Mock netlink replies for zones, cdevs, trips, temp, governor, thresholds, malformed/missing attributes, allocation failure, family resolution failure, and threshold command encoding.
