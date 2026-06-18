# sources/distributed-fs/ceph-client/include/linux/regulator/arizona-ldo1.h

## Purpose

This header defines platform data for the Cirrus/Wolfson Arizona codec LDO1 regulator.

## Important APIs, Types, and Functions

`struct arizona_ldo1_pdata` contains a single `const struct regulator_init_data *init_data` pointer for LDO1 regulator constraints and consumer mapping.

## Control Flow

The parent Arizona MFD or platform code passes the pdata to the LDO1 regulator driver, which uses the init data during regulator registration.

## State and Persistence Behavior

No runtime state is defined here. It is static configuration; actual regulator state is in hardware and regulator core objects.

## Dependencies and Integration Points

It forward-declares `struct regulator_init_data` and integrates with Arizona MFD platform-data plumbing.

## Risks

Null or stale init data can leave LDO1 unconstrained or unavailable to consumers.

## Test Signals

Build/probe tests should validate that Arizona LDO1 registration receives expected constraints and consumer supplies through this structure.
