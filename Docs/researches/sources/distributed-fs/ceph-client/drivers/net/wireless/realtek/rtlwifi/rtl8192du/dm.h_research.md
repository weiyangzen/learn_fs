# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.h

## Purpose
Declares the RTL8192DU dynamic-management entry points.

## Important APIs, Types, And Functions
Exports `rtl92du_dm_init()` for setup and `rtl92du_dm_watchdog()` for periodic runtime maintenance.

## Control Flow
No executable flow. The DU driver calls initialization after hardware bring-up and watchdog through its operation table.

## State And Persistence
No state is owned here. The implementation initializes and updates `rtlpriv` DM structures.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` from including headers. Used by `dm.c`, `hw.c`, and DU module operation wiring.

## Risks
Small header, low direct risk. The only risk is drift between callback prototypes and the operation table users.

## Test Signals
Build success and watchdog invocation on a running DU interface validate the declarations.
