# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_cmd.c

Purpose: Emits GPU batch commands to select and inline-terminate a PXP session on the PXP VCS context.

Important APIs/functions: `intel_pxp_terminate_session()` is the public command path. Helpers emit session selection (`MI_SET_APPID`, protected-memory `MI_FLUSH_DW`), inline `CRYPTO_KEY_EXCHANGE`, wait commands, and commit the request at max priority.

Control flow: Termination creates a request on `pxp->ce`, optionally emits init breadcrumb, reserves ring space for selection+termination+wait, advances the ring, commits/queues the request, waits up to `HZ/5`, and returns command or timeout errors. Disabled PXP returns success without doing work.

State/persistence: No persistent state except use of `pxp->ce` and request lifetime. The hardware session is affected by submitted commands.

Dependencies/integration: Depends on GT request/timeline/ring infrastructure, GPU command definitions, request tracing, and `intel_pxp_session.c` for higher-level teardown.

Risks: Ring-length constants must match emitted dwords. A failed or timed-out request leaves software marking the session invalid but may not complete hardware teardown. Commit bypasses normal caller priority by using `I915_PRIORITY_MAX`.

Test signals: Session teardown logs and timeouts from PXP suspend/restart/debugfs termination. Request tracing shows the termination batch.
