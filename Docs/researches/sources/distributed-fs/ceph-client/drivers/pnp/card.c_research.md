<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/card.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/card.c

Purpose: Support PnP cards: groups of related PnP devices matched by card-level drivers that may claim multiple logical devices.

Important APIs/types/functions: global `pnp_cards` and private `pnp_card_drivers`; `match_card()` checks card ID plus required child device IDs; `pnp_alloc_card()`, `pnp_add_card()`, `pnp_add_card_device()`, `pnp_request_card_device()`, `pnp_release_card_device()`, `pnp_register_card_driver()`, and `pnp_unregister_card_driver()`. Sysfs card attributes expose `name` and `card_id`.

Control flow: protocol backend allocates a card, attaches devices to it, then calls `pnp_add_card()`. Card registration creates the device, adds sysfs files, links it into global/protocol lists, registers contained devices, and probes matching card drivers. A card driver registers a hidden `pnp_driver` link to bind requested child devices. Request/release manually invokes bus probe/bind/release for child devices.

State/persistence: cards maintain ID lists and device lists. `pnp_card_link` tracks a driver/card binding and PM state. Each requested child has `dev->card_link` and driver pointer set until release.

Dependencies/integration: integrates with the PnP bus type, generic driver core, pnp_lock, card protocol lists, and public PnP card driver APIs.

Risks: manual device binding/unbinding is delicate; failure paths must reset `dev->driver` and `card_link`. `card_probe()` returns success when driver probe returns nonnegative and rolls back requested devices on failure. Card sysfs file creation errors are not fatal to card registration beyond attachment return being ignored.

Test signals: multi-function ISA PnP cards, failed card driver probe rollback, suspend/resume state coalescing, and unregister while devices are bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/card.c -->
