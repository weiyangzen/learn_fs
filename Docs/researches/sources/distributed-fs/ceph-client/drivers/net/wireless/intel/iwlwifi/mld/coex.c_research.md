# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/coex.c

## Purpose

`coex.c` handles Bluetooth coexistence initialization and BT activity notifications for MLD.

## Important APIs, Types, and Functions

`iwl_mld_send_bt_init_conf()` sends `BT_CONFIG` with network coexistence mode and MPLUT/high-band retention modules enabled. `iwl_mld_handle_bt_coex_notif()` parses `struct iwl_bt_coex_profile_notif`, treats an all-zero notification as BT-off, updates `mld->bt_is_active`, and invokes `iwl_mld_emlsr_check_bt()`.

## Control Flow

During firmware initialization, the driver sends BT coexistence configuration. Later notification dispatch calls the handler; it ignores no-op state repeats, logs ON/OFF transitions, updates cached activity, and asks MLO/EMLSR code to reevaluate BT-related constraints.

## State and Persistence Behavior

The only local persistent state mutation is `mld->bt_is_active`. Firmware coexistence mode persists after `BT_CONFIG` until firmware reset or reconfiguration.

## Dependencies and Integration Points

The file depends on firmware coexistence API structures, MLD command sending, and EMLSR logic in `mlo.h`.

## Risks and Edge Cases

Using a zeroed whole-structure comparison makes ABI padding and future fields significant. If firmware changes notification layout or adds reserved nonzero fields, BT activity detection may change. The handler does not length-check the packet itself, so dispatch code must guarantee the notification size.

## Test Signals

Validate `BT_CONFIG` is sent on bring-up, BT-on/off notifications toggle `mld->bt_is_active` exactly once per transition, and EMLSR reacts to BT activity. Fuzz notification lengths at the dispatcher if possible.
