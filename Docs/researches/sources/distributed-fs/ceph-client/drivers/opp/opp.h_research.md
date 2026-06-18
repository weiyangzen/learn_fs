<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/opp.h -->
# sources/distributed-fs/ceph-client/drivers/opp/opp.h

## Purpose
`opp.h` is the private header for the OPP implementation. It defines the in-memory representation of OPPs, OPP tables, devices attached to a table, configuration token data, interconnect bandwidth values, internal lifecycle helpers, and debugfs/OF conditional hooks.

## Important APIs, Types, And Functions
Core types are `struct dev_pm_opp_icc_bw`, `struct dev_pm_opp`, `struct opp_device`, `enum opp_table_access`, and `struct opp_table`. `struct dev_pm_opp` stores availability, dynamic/static status, turbo/suspend/removed flags, rates, level, supplies, bandwidth, required OPP pointers, owning table, OF node, and optional debugfs fields. `struct opp_table` stores list nodes, notifier head, device and OPP lists, locks, OF state, current and suspend OPPs, required OPP tables/devices, supported hardware, property name, clocks, regulators, interconnect paths, enable/genpd state, and debugfs fields.

Internal prototypes expose table lookup, allocation, add/remove, key comparison, CPU mask cleanup, indexed table creation, required OPP availability, OF init/clear, and debugfs create/remove/register functions.

## Control Flow
This header has no runtime flow, but it defines the contracts that `core.c`, `of.c`, `cpu.c`, `debugfs.c`, and platform helpers rely on. Conditional inline stubs make OF and debugfs optional without changing core call sites. `lazy_linking_pending()` centralizes the required-opps pending test by checking `opp_table->lazy`.

## State And Persistence
All fields are runtime kernel state. The header defines ownership relationships: OPP tables own OPP entries and `opp_device` records; OPP entries hold references to required OPPs and OF nodes; configs hold an OPP table reference and flags indicating which resources must be unwound. The layout also places debugfs-only fields under `CONFIG_DEBUG_FS`.

## Dependencies And Integration Points
The header includes device, interconnect, kref, list, limits, public PM OPP, and notifier headers. It forward-declares clock and regulator types and binds the OPP implementation to OF, debugfs, CPU, regulator, interconnect, and notifier subsystems.

## Risks
This header is the shared ABI inside the OPP implementation; field semantics must stay synchronized across files. `regulator_count` uses `-1`, `0`, and positive values with distinct meanings, so allocation and parsing code must preserve that convention. The flexible allocation pattern in `_opp_allocate()` depends on field ordering and count values for supplies, rates, and bandwidth. Debugfs and OF fields are conditional, so code must use the provided hooks.

## Test Signals
Build coverage with `CONFIG_OF` and `CONFIG_DEBUG_FS` enabled and disabled is essential. Runtime signals include correct kref release, no list corruption, correct allocations for zero/multiple regulators, clocks, and interconnect paths, and valid required-opps state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/opp.h -->
