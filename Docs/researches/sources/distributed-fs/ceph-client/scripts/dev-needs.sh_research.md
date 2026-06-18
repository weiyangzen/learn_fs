# sources/distributed-fs/ceph-client/scripts/dev-needs.sh

## Purpose
`dev-needs.sh` runs on a booted target and traces device probe dependencies from `/sys/devices` paths, reporting suppliers and parent devices in formats useful for humans, Graphviz, or `tsort`.

## Important APIs, Types, and Functions
Output detail functions include `detail_compat()`, `detail_module()`, `detail_driver()`, `detail_fwnode()`, `detail_graphviz()`, `detail_tsort()`, and `detail_device()`. `add_suppliers()` follows `supplier:*` device links unless disabled, ignoring `sync_state_only` proxy links. `add_parent()` walks to the nearest parent with a driver. `already_seen()` prevents duplicate traversal. `dev_to_detail()` renders sorted unique output.

## Control Flow and State
Flags select detail mode and dependency filters. `CONSUMERS` acts as a breadth-first queue, while `OUT_LIST` stores consumer/supplier pairs. Each consumer is resolved with `realpath`, optionally skipped if it lacks a driver, expanded through suppliers and parent, or marked as root. Output is sorted and deduplicated. State is runtime-only.

## Dependencies and Integration
It depends on Bash arrays, `realpath`, sysfs layout under `/sys/devices`, `sort`, `uniq`, `cut`, and optionally toybox behavior for target devices.

## Risks and Test Signals
Paths are mostly unquoted, so sysfs names with unusual characters would be fragile. The driver filter intentionally skips class-like links by default and can omit useful dependencies. Test modes `-c/-d/-m/-f/-g/-t`, no-driver allowance, excluded parents/devlinks, cycles via sync-state links, and multiple input devices.
