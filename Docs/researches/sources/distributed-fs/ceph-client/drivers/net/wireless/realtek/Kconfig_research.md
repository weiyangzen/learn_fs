# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/Kconfig

## Purpose

This Kconfig file defines the Realtek wireless vendor menu gate `WLAN_VENDOR_REALTEK`. When enabled, it exposes the Realtek subdriver families under `drivers/net/wireless/realtek/`.

## Important APIs, Types, and Functions

The only symbol defined here is `WLAN_VENDOR_REALTEK`, a default-y boolean menu selector. It sources `rtl818x`, `rtlwifi`, `rtl8xxxu`, `rtw88`, and `rtw89` Kconfig files.

## Control Flow

Kconfig processing enters the nested `if WLAN_VENDOR_REALTEK` block only when the vendor menu is enabled. Disabling it hides Realtek-specific questions but does not directly force lower-level symbols off if selected elsewhere.

## State and Persistence Behavior

Persistent state is the user's kernel `.config` choice for `WLAN_VENDOR_REALTEK` and any Realtek child symbols selected below it.

## Dependencies and Integration Points

This file integrates with the Linux wireless Kconfig vendor hierarchy and delegates all actual driver dependencies to child Kconfig files.

## Risks and Edge Cases

Because the vendor symbol is only a visibility gate, build assumptions should not treat it as a hardware-driver dependency. New Realtek families must be sourced here or they will not appear in menuconfig.

## Test Signals

Run `make menuconfig`/`olddefconfig` with the vendor option toggled and confirm all Realtek child menus appear/disappear while direct symbol dependencies remain controlled by their own Kconfig entries.
