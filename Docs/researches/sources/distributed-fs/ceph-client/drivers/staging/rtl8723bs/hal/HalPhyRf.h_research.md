# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.h

## Purpose

`HalPhyRf.h` defines the generic RF power-tracking method enum, callback signatures, configuration structure, and public ODM RF tracking APIs. The file was read as a complete 40-line header.

## Important APIs, Types, and Functions

It defines `enum pwrtrack_method` with `BBSWING`, `TXAGC`, and `MIX_MODE`; callback typedefs `FuncSetPwr`, `FuncLCK`, and `FuncSwing`; `struct txpwrtrack_cfg`; and prototypes for `ConfigureTxpowerTrack`, `ODM_ClearTxPowerTrackingState`, and `ODM_TXPowerTrackingCallback_ThermalMeter`.

## Control Flow

There is no executable flow. The structure is filled by chip-specific code and consumed by the generic thermal callback to invoke set-power, LC calibration, and delta swing table selection.

## State and Persistence Behavior

The header owns no storage. It defines a transient configuration object whose function pointers bridge generic tracking to chip-specific implementations.

## Dependencies and Integration Points

It depends on `struct dm_odm_t`, `struct adapter`, and Realtek integer types from the include chain. It integrates `HalPhyRf.c` with `HalPhyRf_8723B.c`.

## Risks and Edge Cases

Function pointer contracts are not type-safe beyond the typedefs; wrong `RfPathCount`, table sizes, or callback assignment can corrupt thermal tracking. Additions to `enum pwrtrack_method` require switch updates in chip-specific handlers.

## Test Signals

Compile coverage, tests that `ConfigureTxpowerTrack_8723B` fills every callback/size field, and thermal callback tests exercising all three power tracking methods are useful.
