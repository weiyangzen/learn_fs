# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-socinfo.c

## Purpose
This early initcall decodes ASPEED silicon ID and optional chip ID registers and registers a soc_bus device describing the BMC SoC.

## Important APIs, Types, And Functions
`rev_table[]` maps silicon IDs to SoC names. `siliconid_to_name()` masks package/revision bits to find the family name. `siliconid_to_rev()` maps generation/revision fields to A0/A1/A2/A3 strings. `aspeed_socinfo_init()` performs OF lookup, MMIO reads, attribute allocation, and registration.

## Control Flow
At early init, it finds the `aspeed,silicon-id` node, verifies availability, maps resource 0 to read silicon ID, optionally maps resource 1 to read the 64-bit chip ID, reads the root model property, allocates soc attributes, formats ID and serial strings, registers a `soc_device`, and logs the result.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include OF, ioremap from DT resources, sys_soc, and early init ordering.

## Integration Points
Userspace gets machine, family, revision, soc_id, and optional serial number through soc_bus sysfs. Other drivers may use soc_device matching.

## Risks
The code calls `of_device_is_available(np)` without checking whether `np` is NULL, which relies on helper tolerance. Unknown IDs are reported as `"Unknown"` and `"??"`. Allocation failures return `-ENODEV` instead of `-ENOMEM`.

## Test Signals
Boot AST2400/2500/2600/2700 systems, inspect soc_bus attributes, test optional chipid absence, unknown silicon IDs, disabled node behavior, and early init ordering.
