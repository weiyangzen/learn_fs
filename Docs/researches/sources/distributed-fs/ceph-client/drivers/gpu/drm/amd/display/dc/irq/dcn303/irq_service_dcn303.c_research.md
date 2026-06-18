# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c

Purpose: compact DCN 3.0.3 IRQ service for a two-pipe/two-HPD configuration, based on Sienna Cichlid/DCN 3.0.3 register definitions.

Important APIs and functions: `to_dal_irq_source_dcn303()` maps only two vblank, two vline0, two pflip, two vupdate, and two HPD/RX source pairs. `irq_source_info_dcn303` contains two HPD entries, two HPD RX entries, two I2C/DPSINK dummy entries, two underflow dummy entries, and functional pflip/vupdate/vblank/vline0 entries for instances 0 and 1. `dal_irq_service_dcn303_create()` allocates the service.

Control flow: the dispatcher gets a reduced source map. Valid entries use the same generic set/ack and HPD ack behavior as larger DCN tables. Unsupported sources are either absent or dummy, reducing accidental hardware access to non-existent instances.

State and persistence: static const table plus heap service object. The only persistent changes are interrupt control register writes.

Dependencies and integration points: includes Sienna Cichlid IP offsets, DCN 3.0.3 offsets/masks, DCN interrupt IDs, and DCE110 helper definitions. It is selected by DCN303 ASIC initialization.

Risks: reduced source coverage means generic code must not assume six pipes/connectors after this service is installed. Missing DMCUB outbox handling is intentional for this variant; adding firmware paths must audit whether the hardware exposes matching registers.

Test signals: two-display hotplug and page-flip/vblank validation, plus attempts to use unsupported sources should fail through dummy entries rather than touching invalid registers.
