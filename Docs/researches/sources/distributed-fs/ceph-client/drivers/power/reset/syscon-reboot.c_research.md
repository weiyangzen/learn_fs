# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot.c

## Purpose
generic syscon/regmap restart driver with optional Google GS101 mode-specific reset data.

## Important APIs, Types, and Functions
`struct reboot_mode_bits`, `struct reboot_data`, `struct syscon_reboot_context`, restart notifier, and probe.

## Control Flow
probe resolves regmap by phandle or parent, parses priority, either uses match data or DT offset/value/mask fallback, then registers restart; notifier selects mode-specific bits when available and updates the register.

## State and Persistence Behavior
context is devm-managed; syscon reset bits persist until reset.

## Dependencies and Integration Points
OF, MFD_SYSCON, regmap, restart notifier, reboot mode enum values.

## Risks and Edge Cases
bad offset/mask can write unrelated syscon bits; mode-specific table covers only selected reboot modes; `reg` legacy alias complicates bindings; no completion beyond timeout log.

## Test Signals
generic syscon reboot DTs, GS101 warm/soft modes, priority ordering, value/mask fallback, and reboot.
