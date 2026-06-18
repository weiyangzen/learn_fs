# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.h

Purpose: declares the DMUB outbox notification enable helper.

Important API: `dmub_enable_outbox_notification(struct dc_dmub_srv *dmub_srv)` enables outbox1 notifications through the implementation command path.

Control flow role: this small header forward-declares `struct dc_dmub_srv` so users can request notification enablement without including full DMUB service internals.

State and persistence: no owned state. The function it declares changes firmware notification configuration.

Dependencies and integration: integrates with DMUB service startup and event handling code. Its only dependency is the forward declaration of the service structure.

Risks and test signals: API correctness depends on callers passing a live DMUB service. Compile coverage should ensure no include cycles are introduced; runtime signals are successful outbox notification delivery and no command timeouts during initialization.
