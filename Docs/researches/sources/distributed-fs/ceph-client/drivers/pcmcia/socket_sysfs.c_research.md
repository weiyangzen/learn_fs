# sources/distributed-fs/ceph-client/drivers/pcmcia/socket_sysfs.c

Purpose: Provides generic sysfs attributes for PCMCIA socket devices.

Important APIs and functions: Exports `pccard_sysfs_add_socket()` and `pccard_sysfs_remove_socket()`. Attributes include `card_type`, `card_voltage`, `card_vpp`, `card_vcc`, `card_insert`, `card_pm_state`, `card_eject`, `card_irq_mask`, and `available_resources_setup_done`.

Control flow: Show methods read `struct pcmcia_socket` state and format status through `sysfs_emit()`. Store methods validate non-empty input and dispatch synthetic PCMCIA uevents for insert, eject, suspend, resume, or requery. `card_irq_mask` parses a hex mask and intersects it with the socket IRQ mask under `ops_mutex`. `available_resources_setup_done` marks resource setup complete and triggers requery.

State and persistence: Writes mutate the live socket state indirectly through PCMCIA event parsing, `s->irq_mask`, and `s->resource_setup_done`. The sysfs group persists while the socket device is registered.

Dependencies and integration points: Depends on PCMCIA core internals (`cs_internal.h`) and `pcmcia_parse_uevents()`. Called by socket registration paths outside this file.

Risks: User-triggered insert/eject/power events can change runtime card state. `card_irq_mask` only narrows the existing mask, not replaces it, which is intentional but easy to misread. Several show files return `-ENODEV` when no card is present.

Test signals: Attribute group creation/removal, correct output with present and absent cards, insert/eject/requery event effects, suspend/resume via `card_pm_state`, and IRQ mask narrowing under concurrent socket operations.
