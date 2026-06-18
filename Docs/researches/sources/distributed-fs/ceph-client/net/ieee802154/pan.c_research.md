## sources/distributed-fs/ceph-client/net/ieee802154/pan.c

Purpose: PAN association bookkeeping helpers for cfg802154. It answers parent/child association queries, allocates free short addresses, reports whether a device has active associations, and changes maximum association limits.

Important APIs/types/functions: `cfg802154_device_is_associated()` locks `association_lock` and checks for any parent or child entries. `cfg802154_device_is_parent()` and `cfg802154_device_is_child()` require the lock held and compare target extended addresses against parent/children. `cfg802154_get_free_short_addr()` randomly chooses a short address avoiding broadcast, unspecified, the device's own short address, parent, and children. `cfg802154_set_max_associations()` updates `wpan_dev->max_associations` and returns the old value.

Control flow and state: association state lives in `wpan_dev->parent`, `wpan_dev->children`, `wpan_dev->nchildren`, and `wpan_dev->max_associations`, protected by `association_lock`. Matching intentionally rejects short-address input because the PAN management helpers expect extended addresses for identity checks.

Dependencies and integration points: used by modern nl802154 to block PAN ID/short address changes while associated and set max associations. Exported helpers are available to drivers/mac802154 code.

Risks: `cfg802154_get_free_short_addr()` contains a `continue` inside `list_for_each_entry()` that only advances the list loop, not the outer random-selection loop, so collision handling with child addresses deserves close review/testing. Random selection can loop indefinitely only under pathological/full address-space conditions.

Test signals: parent/child lookup with extended and short targets, association-present checks, max-association update, short-address allocation avoiding reserved/self/parent/children, and lockdep assertions for helpers requiring held lock.
