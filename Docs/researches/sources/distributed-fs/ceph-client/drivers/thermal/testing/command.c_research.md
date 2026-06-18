# sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/command.c` is the command parser and module entry for the thermal core debugfs testing facility. It exposes `/sys/kernel/debug/thermal-testing/command` so developers can create, modify, register, and unregister synthetic thermal zones. The source was read as a complete 211-line file.

## Important APIs, Types, and Functions

The exported global is `struct dentry *d_testing`. Important local pieces are `enum tt_commands`, `tt_command_strings[]`, `tt_command_exec()`, `tt_command_process()`, `tt_command_write()`, `thermal_testing_init()`, and `thermal_testing_exit()`. It calls zone helpers declared in `thermal_testing.h`: `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`.

## Control Flow

Module init creates the `thermal-testing` debugfs directory and a write-only `command` file. Writes are single-shot (`*ppos` must be zero), capped at 15 bytes plus NUL, copied from userspace, trimmed, split on optional `:`, matched against known command strings, and dispatched to the zone layer. Module exit removes the debugfs root and asks the zone layer to unregister/free all templates.

## State and Persistence Behavior

The file owns only the debugfs root pointer. Test-zone state lives in `zone.c` and is volatile; it disappears at module unload or reboot.

## Dependencies and Integration Points

It depends on debugfs, module init/exit, and the thermal testing zone API. It is meant for controlled test environments and uses debugfs rather than sysfs ABI.

## Risks and Edge Cases

The command buffer is deliberately small; invalid or too-long commands fail with `-EINVAL` or `-E2BIG`. Commands requiring an argument pass `NULL` when no colon is present; the zone helpers must reject that safely. `debugfs_create_dir()` errors are only checked with `IS_ERR`, and init returns 0 even if debugfs creation fails, which is normal for debug-only facilities but affects test availability.

## Test Signals

Manual debugfs tests should cover `addtz`, `deltz:<id>`, `tzaddtrip:<id>`, `tzreg:<id>`, and `tzunreg:<id>`, invalid commands, oversized writes, nonzero offset writes, and module unload cleanup after registered zones exist.
