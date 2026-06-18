# sources/distributed-fs/ceph-client/drivers/power/reset/arm-versatile-reboot.c

## Purpose
ARM Integrator, Versatile, and RealView syscon restart driver.

## Important APIs, Types, and Functions
global `syscon_regmap`, `versatile_reboot_type`, `versatile_reboot()`, and `versatile_reboot_probe()` select reset register sequences by compatible string.

## Control Flow
probe finds the first matching syscon node, stores match data, converts it to a regmap, and registers a high-priority restart notifier; restart unlocks the syscon and writes board-specific reset values.

## State and Persistence Behavior
global regmap/type persist after `device_initcall`; hardware reset registers persist only until reset.

## Dependencies and Integration Points
OF matching, syscon/regmap, restart notifier, ARM barrier `dsb()`.

## Risks and Edge Cases
single global instance and no unregister path; wrong compatible data writes the wrong reset sequence; regmap write failures are ignored in notifier context.

## Test Signals
boot each supported board compatible, verify restart, missing syscon failure, and register write traces.
