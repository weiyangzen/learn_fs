# sources/distributed-fs/ceph-client/include/linux/regulator/mt6358-regulator.h

## Purpose

This header enumerates regulator IDs for MediaTek MT6358 and MT6366 PMIC variants.

## Important APIs, Types, and Functions

`enum` blocks define MT6358 IDs from `VDRAM1` through `VSIM2`, ending with `MT6358_ID_RG_MAX`, and MT6366 IDs with a similar but variant-specific rail set ending with `MT6366_ID_RG_MAX`. Max macros expose both counts.

## Control Flow

The regulator driver selects the appropriate enum/descriptor table for the detected PMIC variant and registers rails by ID.

## State and Persistence Behavior

No runtime state is in the header. Hardware registers and regulator core objects hold rail state.

## Dependencies and Integration Points

It is standalone and integrates with MT6358/MT6366 regulator drivers and bindings.

## Risks

Variant-specific enum differences can cause descriptor mismatches if the wrong table is selected. Explicit numbering around `MT6358_ID_VDRAM2 = 9` must be preserved.

## Test Signals

Tests should cover both variants, descriptor counts, supply matching, and rail capability differences.
