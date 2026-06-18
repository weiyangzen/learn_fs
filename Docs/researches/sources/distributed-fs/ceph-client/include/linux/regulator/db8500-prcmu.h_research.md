# sources/distributed-fs/ceph-client/include/linux/regulator/db8500-prcmu.h

## Purpose

This header enumerates DB8500 PRCMU-managed power domain regulators and switches.

## Important APIs, Types, and Functions

`enum db8500_regulator_id` lists voltage regulators (`VAPE`, `VARM`, `VMODEM`, `VPLL`, `VSMPS1-3`, `VRF1`) and switch regulators for DSP/APIPE/SGA/B2R2/MCDE/ESRAM domains, ending with `DB8500_NUM_REGULATORS`.

## Control Flow

Drivers use the enum IDs to index descriptor tables and register PRCMU-controlled rails/switches with the regulator core.

## State and Persistence Behavior

No state is defined here. Runtime state resides in PRCMU firmware/hardware and regulator core objects.

## Dependencies and Integration Points

This header is standalone. It integrates with ST-Ericsson DB8500 platform regulator drivers and consumer supply mappings.

## Risks

Changing enum order breaks descriptor indexing and board data. Mistaking switch domains for voltage regulators can expose unsupported operations.

## Test Signals

Build/probe tests should ensure every ID has a descriptor, correct operation capabilities, and expected consumer mappings.
