# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.c

Purpose: Implements the GSC command streamer backend for PXP firmware communication on platforms with a GSC engine.

Important APIs/functions: `intel_pxp_gsccs_init()`, `intel_pxp_gsccs_fini()`, `intel_pxp_gsccs_is_ready_for_sessions()`, `intel_pxp_gsccs_create_session()`, and `intel_pxp_gsccs_end_arb_fw_session()`. Internal core is `gsccs_send_message()` plus pending-retry wrapper.

Control flow: Init allocates and pins a large HECI packet VMA and a batch-buffer VMA, creates a GSC context using the GT VM, seeds a host session handle, then initializes PXP hardware under RPM. Message send builds a GSC MTL header, copies input into the packet buffer, submits a nonpriv HECI packet on the GSC engine, validates reply marker/status, handles pending replies by retrying with firmware's message handle, and copies bounded output. Fini sends cleanup for the host session handle, releases context and VMAs, and disables hardware under RPM.

State/persistence: `pxp->gsccs_res` stores host session handle, context, packet/batch VMAs, and CPU mappings. `platform_cfg_is_bad` is set on selected firmware statuses. Retry state is per message.

Dependencies/integration: Depends on GSC firmware/HECI submit helpers, GEM internal objects, i915 VMAs, GT GSC engine, PXP command ABI 4.2/4.3, runtime PM, and HuC/GSC readiness checks.

Risks: Buffer size calculations must include GSC headers and firmware maximums. Pending replies can take up to the configured retry budget. Cleanup messages with empty packets are special and must be sent before dropping resources. Firmware platform-config errors are persistent until reconfiguration. Mutex `tee_mutex` serializes this backend too, so long firmware waits block other PXP messaging.

Test signals: Logs for invalid validity marker, GSC reply status, pending timeout, session init/invalidate statuses, and readiness via HuC authenticated plus GSC proxy init done.
