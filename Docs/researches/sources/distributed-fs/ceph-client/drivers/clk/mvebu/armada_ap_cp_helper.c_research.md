# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.c

Purpose: helper for Armada AP/CP clock drivers to create unique clock names from syscon resource addresses.

Important APIs/functions: `ap_cp_unique_name` returns a devm-managed string formatted as `<resource-start>-<name>`.

Control flow: if `name` is NULL, returns NULL. Otherwise it converts the first address resource of `np` to `struct resource` and formats the start address plus requested base name.

State and persistence: returned strings are device-managed allocations owned by `dev`.

Dependencies and integration: used by AP806, AP CPU, and CP110 clock drivers to avoid duplicate names when multiple AP/CP instances exist.

Risks: return value of `of_address_to_resource` is ignored; malformed nodes may produce an uninitialized or stale resource. Names depend on physical address stability in DT.

Test signals: multiple CP110/AP instances producing distinct clock names, fault-injection for missing `reg`, and memory lifetime via devm teardown.
