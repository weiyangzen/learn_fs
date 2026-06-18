# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_btcoex.c

## Purpose
Small core wrapper layer connecting RTL8723BS MLME/power-save behavior to the HAL Bluetooth coexistence implementation.

## Important APIs, Types, And Functions
Defines `rtw_btcoex_MediaStatusNotify()`, `rtw_btcoex_HaltNotify()`, `rtw_btcoex_RejectApAggregatedPacket()`, `rtw_btcoex_LPS_Enter()`, and `rtw_btcoex_LPS_Leave()`.

## Control Flow
Media-status notification downloads reserved pages when connecting in AP mode, then forwards status to HAL coexistence. Halt notification returns early if the adapter is not up or surprise-removed, then calls HAL halt handling. AP aggregation rejection disables accepting ADDBA requests and sends DELBA to the current BSSID station; disabling re-allows ADDBA. LPS enter marks power saving, asks HAL for coexistence LPS value, and enters minimum power-save mode. LPS leave restores active power mode, waits for RF on, and clears the power-saving flag.

## State And Persistence
Mutates `mlmeext_info.accept_addba_req`, station aggregation state through DELBA, and `pwrctrl_priv` power-save flags/mode. No persistent state.

## Dependencies And Integration Points
Depends on Realtek adapter structures, HAL BT coexistence callbacks, MLME AP-state checks, reserved-page hardware variable, station lookup, DELBA transmission, and power-control APIs.

## Risks
Aggregation rejection only finds a station by current BSSID, which may not cover all AP-mode clients. Power-save transitions are driven by coexistence policy and can interact with normal MLME power management. Halt notification silently skips on device-down/surprise-removed paths.

## Test Signals
BT coexistence media connect/disconnect in AP and STA modes, reserved-page download on AP connect, HAL halt calls, ADDBA rejection and DELBA side effects, LPS enter/leave transitions, RF-on check timeout, and surprise removal.
