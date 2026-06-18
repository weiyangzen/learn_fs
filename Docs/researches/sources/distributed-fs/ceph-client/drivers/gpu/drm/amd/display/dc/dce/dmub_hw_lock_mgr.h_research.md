# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.h

Purpose: declares the DMUB hardware-lock command and policy helpers used by DC hardware sequencing.

Important APIs: `dmub_hw_lock_mgr_cmd()` emits ring-buffer lock/unlock commands. `dmub_hw_lock_mgr_inbox0_cmd()` emits inbox0 lock commands. `should_use_dmub_inbox1_lock()` and `should_use_dmub_inbox0_lock_for_link()` choose transport. `dmub_hw_lock_mgr_does_link_require_lock()` and `dmub_hw_lock_mgr_does_context_require_lock()` expose feature-policy checks.

Control flow role: the header documents that inbox0 is not functionally equivalent to inbox1 because DMUB will not own programming of the relevant locking registers. This distinction guides callers that need either DMUB-owned sequencing or a lighter DMU interlock.

State and persistence: no header-owned state. The APIs operate on caller-owned DC, link, context, and DMUB service objects and on caller-provided lock flag structures.

Dependencies and integration: includes `dc_dmub_srv.h` and `core_types.h`, pulling in DC, link, state, and DMUB command types. Integrates with PSR/Replay commit paths and hardware sequencing code.

Risks and test signals: callers must not pass stale link/context pointers and must release locks through the same intended mechanism. Compile tests should verify command-union type visibility. Runtime tests should validate policy decisions for null links, unsupported DMUB, supported inbox0 metadata, PSR/Replay feature combinations, and release handling.
