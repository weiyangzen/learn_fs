# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.h

## Purpose

This header declares the Vega12 BACO state transition entry point.

## Important APIs, Types, and Functions

It includes `smu9_baco.h` for `enum BACO_STATE` and declares `vega12_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`.

## Control Flow, State, and Persistence

The header contains no state. The declared function mutates hardware BACO state through register command tables and SMC messages in the C implementation.

## Dependencies and Integration Points

It depends on the shared SMU9 BACO declarations and is intended for Vega12 hwmgr integration code that needs to enter or leave BACO during power transitions.

## Risks and Test Signals

Build tests should ensure `struct pp_hwmgr` and `enum BACO_STATE` are visible through included headers in all translation units that include this file. Runtime tests should exercise both `BACO_STATE_IN` and `BACO_STATE_OUT` through the exported function rather than duplicating command sequences elsewhere.
