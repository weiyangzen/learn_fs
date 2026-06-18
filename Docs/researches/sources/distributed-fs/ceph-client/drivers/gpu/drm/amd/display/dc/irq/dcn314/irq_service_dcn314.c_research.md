# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c

Purpose: DCN 3.1.4 IRQ service. It is structurally close to DCN31 but uses DCN 3.1.4 register offsets and a local `DCN_BASE__INST0_SEG2` override.

Important APIs and functions: `to_dal_irq_source_dcn314()` maps six standard display source IDs, HPD/RX by ext_id, and DMCUB low-priority outbox. The table defines HPD/RX for instances 0 through 4, pflip for 0 through 3, vupdate/vblank/vline0 for the supported OTG range, dummy placeholders for unsupported PFLIP5/6 and some vline1 entries, and DMCUB OUTBOX1.

Control flow: same shared path: source translation, table lookup, optional HPD-specific ack, otherwise generic register writes.

State and persistence: static const table and transient heap wrapper. Persistent state is in hardware interrupt enable/ack registers.

Dependencies and integration points: depends on DCN 3.1.4 offset/mask headers and the shared DCE110/IRQ framework. It is the binding point between DCN314 interrupt IDs and common DRM display interrupt handling.

Risks: base-segment overrides are brittle; wrong base values will compile but program incorrect registers. Instance count assumptions around HPD5/6, PFLIP5/6, and vline1 must match actual resource capabilities.

Test signals: runtime IRQ smoke tests on DCN314 hardware, especially DMCUB outbox, HPD, page flip, and vblank after modeset.
