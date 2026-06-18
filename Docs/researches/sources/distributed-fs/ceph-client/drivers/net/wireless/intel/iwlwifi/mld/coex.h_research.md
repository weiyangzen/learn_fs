# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.h

## Purpose

`coex.h` declares MLD Bluetooth coexistence APIs.

## Important APIs, Types, and Functions

It exposes `iwl_mld_send_bt_init_conf()` and `iwl_mld_handle_bt_coex_notif()`.

## Control Flow

Firmware bring-up code calls the init function; notification dispatch calls the handler for BT coexistence profile notifications.

## State and Persistence Behavior

The header has no state. The implementation mutates `mld->bt_is_active` and sends persistent firmware coexistence configuration.

## Dependencies and Integration Points

It includes `mld.h` for `struct iwl_mld` and uses `struct iwl_rx_packet` from common firmware RX types through included headers.

## Risks and Edge Cases

Header risks are limited to prototype drift and ensuring consumers include it under the same feature conditions as `coex.c`.

## Test Signals

Build all users and verify notification dispatch links against the handler.
