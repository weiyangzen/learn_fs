# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp.c

Purpose: Top-level Protected Xe Path lifecycle and policy implementation: capability selection, backend setup, hardware enable/disable, session start/end orchestration, protected-object key validation, and invalidation of protected contexts after key loss.

Important APIs/functions: `intel_pxp_is_supported()`, `intel_pxp_is_enabled()`, `intel_pxp_is_active()`, `intel_pxp_init()`, `intel_pxp_fini()`, `intel_pxp_start()`, `intel_pxp_end()`, `intel_pxp_init_hw()`, `intel_pxp_fini_hw()`, `intel_pxp_get_readiness_status()`, `intel_pxp_get_backend_timeout_ms()`, `intel_pxp_key_check()`, `intel_pxp_invalidate()`, and `intel_pxp_mark_termination_in_progress()`.

Control flow: Init picks a control GT either for full protected content or a TEE link needed by HuC authentication. Full PXP creates session-management state, a pinned VCS context, and either a GSC-CS backend or a MEI TEE component backend. Start waits for firmware/backend readiness, drives a teardown/restart path if the arb session is invalid, then expects worker completion to recreate the session. End synchronously tears down the arb session, disables hardware, and drops RPM. Invalidation scans GEM contexts, bans protected-content contexts, and releases their PXP wakeref.

State/persistence: `i915->pxp` is allocated and freed here. `arb_is_valid`, `key_instance`, `platform_cfg_is_bad`, `termination`, `session_events`, `ce`, `ctrl_gt`, and `kcr_base` define persistent subsystem state. `key_instance` is incremented on new arb-session creation and is used to reject objects encrypted with stale keys.

Dependencies/integration: Integrates with GT engines, VCS pinned contexts, KCR registers, PXP IRQ/session/PM modules, GSC-CS backend, MEI TEE backend, HuC firmware dependencies, runtime PM, GEM context lists, and protected-content UAPI semantics.

Risks: Incorrect backend selection can expose unavailable PXP to userspace or break HuC loading. Session validity is software-tracked because hardware state may remain "in play" after keys are gone. Context invalidation races with execbuf are acknowledged and mitigated by fast banning. Readiness return values are UAPI-visible and must remain compatible.

Test signals: Debugfs `pxp/info`, PXP status GET_PARAM, protected-object execution failures (`-ENODEV`, `-ENOEXEC`), session timeout logs, and suspend/runtime PM paths that invalidate sessions.
