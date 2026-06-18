<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h

## Purpose
Defines the private data structures, exported function declarations, and descriptor-construction macros shared by MC13xxx regulator drivers.

## Important APIs, Types, And Functions
`struct mc13xxx_regulator` combines a `struct regulator_desc` with enable and voltage selector register metadata. `struct mc13xxx_regulator_priv` stores the parent `struct mc13xxx`, POWERMISC power-gate state, descriptor table pointer, regulator count, and a flexible array of registered regulator devices. Macros `MC13xxx_DEFINE`, `MC13xxx_FIXED_DEFINE`, `MC13xxx_GPO_DEFINE`, `MC13xxx_DEFINE_SW`, and `MC13xxx_DEFINE_REGU` build indexed descriptor entries from per-chip register-token prefixes.

## Control Flow
The header has no runtime control flow. Its macros expand in MC13783/MC13892 sources to populate descriptor arrays with names, voltage tables, ops, IDs, register addresses, enable bits, selector shifts, and selector masks.

## State And Persistence
State shape is defined here but allocated by chip drivers. `powermisc_pwgt_state` exists to persist the logical state of inverted power-gate bits across POWERMISC read/modify/write cycles during the device lifetime.

## Dependencies And Integration Points
Depends on regulator driver types and platform-device declarations when OF helpers are enabled. It is the contract between the shared MC13xxx core and chip-specific tables.

## Risks And Test Signals
Risks are macro token-pasting mistakes, descriptor IDs diverging from array indexes, and flexible-array allocation size mismatches. Test by compiling both OF and non-OF configurations, checking generated descriptors for each chip, and verifying `struct_size(priv, regulators, num_regulators)` allocations match use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h -->
