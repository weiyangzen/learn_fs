# sources/distributed-fs/ceph-client/drivers/bus/simple-pm-bus.c

## Purpose
This generic transparent bus driver adds runtime/system PM around simple DT bus nodes that need clocks enabled while their children are active. It also safely declines to manage pure `simple-bus`-style nodes when this driver is not the most specific binding.

## Important APIs, Types, and Functions
`struct simple_pm_bus` stores all clocks returned by `devm_clk_bulk_get_all()`. `simple_pm_bus_probe()` handles override and match specificity checks, allocates state, enables runtime PM, and populates children. Runtime PM callbacks use `clk_bulk_prepare_enable()` and `clk_bulk_disable_unprepare()`. System sleep callbacks force runtime PM suspend/resume when the bus is managed.

## Control Flow
Probe returns immediately for `driver_override` bindings. For `ONLY_BUS` match entries, probe only proceeds if that compatible is the first compatible string; otherwise it returns `-ENODEV` so a more specific driver can bind. Managed buses acquire all clocks, enable PM, and populate children using optional auxdata. Remove mirrors only PM disable because child devices are handled by platform core/devm lifetime.

## State and Persistence
The only runtime state is the clock bulk pointer/count. Clock state is controlled by runtime PM and restored through force suspend/resume. No hardware registers are programmed directly.

## Dependencies and Integration Points
It depends on OF matching/population, CCF bulk clock APIs, runtime PM, and platform devices. It is shared infrastructure for SoC buses with child devices but minimal bus-specific logic.

## Risks and Test Signals
Risks include accidentally binding to a node with a more specific driver if compatible ordering is wrong, leaving children populated after failed later work, and clock naming/availability problems. Test signals are child devices probing only under intended nodes, balanced runtime PM usage, clock enable/disable transitions during autosuspend, and no regression for plain `simple-bus` nodes.
