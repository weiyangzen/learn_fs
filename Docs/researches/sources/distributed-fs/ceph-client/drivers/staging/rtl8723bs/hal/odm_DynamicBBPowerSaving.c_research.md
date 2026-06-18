# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DynamicBBPowerSaving.c

## Purpose

`odm_DynamicBBPowerSaving.c` implements a baseband RF-saving mode that rewrites selected BB registers when RSSI is high enough, and restores saved values when RSSI drops or normal mode is forced. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

The public functions are `odm_DynamicBBPowerSavingInit` and `ODM_RF_Saving`. The key state is `struct ps_t` inside `dm_odm_t`.

## Control Flow

Initialization sets previous/current CCA and RF states to sentinel maxima and clears saved register state. `ODM_RF_Saving` chooses RSSI thresholds, snapshots registers `0x874`, `0xc70`, `0x85c`, and `0xa74` on first use, selects RF save/normal state with hysteresis unless forced normal, and writes either the save-mode register values or the saved normal values when state changes.

## State and Persistence Behavior

`ps_t` persists saved register values, RSSI minimum, initialization flag, and previous/current RF state. Hardware register changes persist until the next state transition or adapter reset.

## Dependencies and Integration Points

It depends on `dm_odm_t->RSSI_Min`, `PatchID`, PHY BB register access, and the ODM support flag path that can call `dm_RF_Saving`. Initialization is invoked from `ODM_DMInit`.

## Risks and Edge Cases

The first snapshot occurs lazily at the first `ODM_RF_Saving` call, so if the hardware is already modified before that call, restore values may be wrong. RSSI `0xff` produces `RF_MAX` and no meaningful save/normal action. The function uses hard-coded registers and magic values.

## Test Signals

Tests should validate initialization, first-call register snapshots, high/low RSSI hysteresis, force-normal behavior, FUNAI patch thresholds, and exact register writes for save and restore transitions.
