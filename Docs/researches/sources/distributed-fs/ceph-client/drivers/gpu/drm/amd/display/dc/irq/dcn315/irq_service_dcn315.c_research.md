# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c

Purpose: DCN 3.1.5 IRQ service variant, similar to DCN314 but with explicit DCN base segment definitions for segments 0 through 5.

Important APIs and functions: `to_dal_irq_source_dcn315()` maps standard six-ID display events, HPD/RX ext IDs, and DMCUB low-priority outbox. `irq_source_info_dcn315` covers HPD/RX instances 0 through 4, pflip 0 through 3, vupdate/vblank/vline0 entries, dummy unsupported sources, and DMCUB OUTBOX1. `dal_irq_service_dcn315_create()` is the factory.

Control flow: common IRQ source translation and table-driven set/ack. HPD ack uses `hpd0_ack()`, other real sources use generic register fields.

State and persistence: static const table and allocated service object. The base segment macros determine the persistent MMIO locations touched during enable/ack.

Dependencies and integration points: DCN 3.1.5 offset/mask headers, DCE110 IRQ helpers, DCN interrupt IDs, and the shared IRQ service. Integrates ASIC interrupt wiring with DC core.

Risks: hard-coded base segments are high risk when reused across steppings. Table entries for unsupported sources intentionally dummy out several enum slots; callers must not assume all six translated source IDs have active hardware entries.

Test signals: hardware IRQ tests for DMCUB outbox, HPD/RX, vblank, and page flips; build testing for register macro compatibility.
