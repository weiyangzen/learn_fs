# sources/distributed-fs/ceph-client/drivers/reset/reset-tenstorrent-atlantis.c

Purpose: Tenstorrent Atlantis PRCM auxiliary reset driver for RCPU/LSIO peripheral resets backed by a parent PRCM regmap.

Important APIs/types/functions: `atlantis_reset_data` maps register, bit, and polarity; `atlantis_reset_controller_data` selects the reset table. `atlantis_reset_update()` computes active-low value and writes with `regmap_update_bits()`. `atlantis_reset_probe()` gets the parent regmap and registers reset ops for auxiliary device `atlantis_prcm.rcpu-reset`.

Control flow: parent PRCM creates an auxiliary device; probe binds by auxiliary ID, uses `driver_data` for the table, and registers reset controls. Runtime assert/deassert updates one mapped bit.

State and persistence: static reset tables and parent regmap; hardware bits store state. Device-managed allocation owns the controller.

Dependencies and integration: auxiliary bus, parent regmap, Atlantis clock/reset dt-bindings, reset-controller framework.

Risks and test signals: no local `.status` implementation. Trusts reset core for ID bounds and parent for regmap lifetime. Test auxiliary-device matching, parent regmap absence, active-low polarity, and all binding IDs against table coverage.
