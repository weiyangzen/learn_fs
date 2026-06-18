# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_types.h

Purpose: Defines persistent PXP subsystem state shared by top-level logic, PM, IRQ/session code, and firmware backends.

Important APIs/types: `struct intel_pxp`, nested `gsccs_session_resources`, session event bit macros `PXP_TERMINATION_REQUEST`, `PXP_TERMINATION_COMPLETE`, `PXP_INVAL_REQUIRED`, and `PXP_EVENT_TYPE_IRQ`.

Control flow: No executable flow; comments describe ownership and locking. `tee_mutex` protects component binding and messaging; `arb_mutex` protects arb session start; `termination` completion coordinates teardown; `session_events` is protected by `gt->irq_lock`.

State/persistence: Holds control GT, platform bad-config latch, KCR base, GSC-CS resources, MEI component/device link state, kernel PXP context, arb validity, key instance, stream command object, hardware invalidation flag, IRQ enabled flag, completion, work item, and event bits.

Dependencies/integration: Forward declares GT/context/component/i915 types and includes Linux completion/mutex/workqueue APIs. It is the central shared contract across all PXP files.

Risks: Multiple locks protect different fields; mixing them incorrectly can race backend messages, session starts, IRQ event updates, or PM transitions. `platform_cfg_is_bad` intentionally persists after firmware reports platform issues. `arb_is_valid` is a software truth distinct from hardware session-in-play bits.

Test signals: Debugfs exposes active/key instance; logs and completion waits reveal event/session state transitions.
