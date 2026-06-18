# sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/testing/thermal_testing.h` is the small internal header shared by the thermal testing command and zone modules. The source was read as a complete 11-line file.

## Important APIs, Types, and Functions

It declares the shared debugfs root `d_testing` and the zone-management functions `tt_add_tz()`, `tt_del_tz()`, `tt_zone_add_trip()`, `tt_zone_reg()`, `tt_zone_unreg()`, and `tt_zone_cleanup()`.

## Control Flow

There is no runtime flow. The declarations let `command.c` dispatch debugfs commands to `zone.c`.

## State and Persistence Behavior

The header does not own state. It exposes state owned by `command.c` and functions managing state in `zone.c`.

## Dependencies and Integration Points

The file requires `struct dentry` to be visible to C users that include it after debugfs headers. It forms the internal ABI of `thermal-testing.o`.

## Risks and Edge Cases

Because this is an internal header, signature drift between command and zone code will be caught at compile time. It has no include guard, but the small declarations are harmless in current usage; adding definitions would require a guard.

## Test Signals

Compilation of `command.o` and `zone.o` together validates this file. Runtime command dispatch confirms the prototypes remain correct.
