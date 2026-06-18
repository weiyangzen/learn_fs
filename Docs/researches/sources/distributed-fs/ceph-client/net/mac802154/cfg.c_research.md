# sources/distributed-fs/ceph-client/net/mac802154/cfg.c

## Purpose
`cfg.c` implements the `cfg802154_ops` bridge between nl802154/cfg802154 user requests and mac802154 internals. It handles virtual interface creation/removal, suspend/resume, PHY settings, per-interface MAC parameters, scans, beaconing, association/disassociation, and optional experimental LLSEC table operations.

## Important APIs, Types, And Functions
The exported object is `mac802154_config_ops`. Important functions include `ieee802154_add_iface()`, `ieee802154_del_iface()`, `ieee802154_set_channel()`, `ieee802154_set_cca_mode()`, `ieee802154_set_cca_ed_level()`, `ieee802154_set_tx_power()`, `ieee802154_set_pan_id()`, `ieee802154_set_short_addr()`, CSMA/retry/LBT/ACK setters, `mac802154_trigger_scan()`, `mac802154_abort_scan()`, `mac802154_send_beacons()`, `mac802154_stop_beacons()`, `mac802154_associate()`, and `mac802154_disassociate()`. PM hooks are `ieee802154_suspend()` and `ieee802154_resume()` under `CONFIG_PM`.

Experimental LLSEC callbacks wrap `mac802154_llsec_*` functions under `sdata->sec_mtx` for key, device, device-key, security-level, and parameter operations.

## Control Flow
Most setters assert RTNL, compare the requested value to current software state, call a driver operation when hardware-backed, and update software state only on success. Channel changes reject attempts while scanning or beaconing and update PHY duration calculations after a successful driver channel set.

Suspend holds/synchronizes queues and stops hardware if any interface is open, then marks `local->suspended`. Resume restarts hardware with the current filtering level/address filter when needed, releases the queue, and clears suspended state.

Association allocates a parent PAN device, preloads PAN ID filtering for hardware address-filter devices so association responses are not dropped, performs the association exchange, optionally installs the assigned short address in hardware, and commits `wpan_dev` parent/PAN/short-address state. Disassociation handles either parent or child relationships, sends notification frames, removes child list entries, resets local parent/PAN/short address when leaving a parent, and restores max associations.

## State And Persistence
Runtime state lives in `wpan_phy`, `wpan_dev`, `ieee802154_local`, and `ieee802154_sub_if_data`. The file mutates current channel/page, CCA mode, ED threshold, TX power, PAN ID, short address, CSMA/backoff/retry/LBT/ACK defaults, association parent/children lists, and LLSEC tables. None persists beyond device/module lifetime.

## Dependencies And Integration Points
The file depends on cfg802154/nl802154, RTNL locking, `driver-ops.h`, `ieee802154_i.h`, scan/beacon/MAC-command helpers, and LLSEC implementation. It is registered by mac802154 main code through `mac802154_config_ops` and called from nl802154/cfg802154 control paths.

## Risks And Edge Cases
Setters that only update software state do not call driver ops even when hardware could later need the value; startup in `iface.c` must replay supported hardware-backed parameters. Association rollback resets PAN ID on failures but short-address rollback after a later failure depends on the failure point. Disassociation from a parent sends child notifications and deletes list nodes without decrementing `nchildren` in the parent path, which should be checked against cfg802154's child accounting expectations. PM resume returns immediately on `drv_start()` failure before releasing held queues or clearing suspended state.

## Test Signals
Tests should cover RTNL assertions, channel change rejection during scan/beacon, successful and failed driver setter paths, PM suspend/resume with open and closed devices, association rollback at each failure point, disassociation parent/child paths, LLSEC mutex wrapping, and module build with/without `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.
