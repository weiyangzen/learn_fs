# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.c

Purpose: Registers PXP debugfs controls for inspecting PXP state and forcing a termination event.

Important APIs/functions: `intel_pxp_debugfs_register()`, `pxp_info_show()`, and the `terminate_state` simple attribute setter.

Control flow: Registration creates `pxp/info` and `pxp/terminate_state` under DRM debugfs when PXP is supported. Reading `info` prints enabled/active state and key instance. Writing `terminate_state` simulates a termination interrupt under `gt->irq_lock`, then waits for the PXP termination completion with backend-specific timeout.

State/persistence: Does not own state; observes `arb_is_valid`, `key_instance`, and uses `termination` completion. The setter mutates session events through the IRQ handler.

Dependencies/integration: Uses debugfs, DRM seq printers, PXP IRQ/session state, and backend timeout helpers.

Risks: Debugfs termination intentionally disrupts protected sessions and invalidates contexts. It requires active PXP and may timeout if worker/backend completion fails.

Test signals: Manual debugfs reads and writes; `terminate_state` can exercise IRQ/session recovery without real hardware interrupt injection.
