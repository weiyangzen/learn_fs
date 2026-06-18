# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.h

## Purpose
`vendor_cmd.h` defines the public constants and declaration for wlcore TI vendor-command registration. It names the TI OUI, smart-config command IDs, smart-config attribute IDs, and smart-config event IDs used by cfg80211 userspace APIs.

## Important APIs And Types
- `TI_OUI` is `0x080028`, the vendor identifier stored in nl80211 vendor command/event metadata.
- `wlcore_set_vendor_commands(struct wiphy *wiphy)` is declared for kernel builds and implemented in `vendor_cmd.c`.
- `enum wlcore_vendor_commands` defines `SMART_CONFIG_START`, `SMART_CONFIG_STOP`, and `SMART_CONFIG_SET_GROUP_KEY`.
- `enum wlcore_vendor_attributes` defines attributes for frequency, PSK, SSID, group ID, and group key. The current C implementation uses group ID and group key, with a policy entry for frequency.
- `enum wlcore_vendor_events` defines smart-config sync and decode events.

## Control Flow And Integration
The header is included by `vendor_cmd.c` and by wlcore registration code. Userspace identifies commands by the TI OUI plus subcommand number; cfg80211 dispatches to handlers installed by `wlcore_set_vendor_commands()`.

## State And Persistence Behavior
There is no mutable state. The enum numeric order is ABI-significant for userspace and should be treated as stable.

## Dependencies
The function declaration uses `struct wiphy` from cfg80211 when `__KERNEL__` is defined. Attribute lengths and parsing policy live in `vendor_cmd.c`.

## Risks And Test Signals
Changing enum order or OUI breaks userspace ABI. Adding attributes requires matching netlink policy updates in `vendor_cmd.c`. Tests should confirm command IDs and event IDs match userspace tooling and that unsupported/unused attributes are either ignored intentionally or documented.
