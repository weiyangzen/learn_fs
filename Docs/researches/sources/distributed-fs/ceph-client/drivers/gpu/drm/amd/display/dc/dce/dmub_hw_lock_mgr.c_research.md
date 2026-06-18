# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_hw_lock_mgr.c

Purpose: centralizes decisions and command emission for DMUB hardware-lock coordination used by PSR/Replay and related embedded-panel paths.

Important functions: `dmub_hw_lock_mgr_cmd()` sends inbox1/ring-buffer `DMUB_CMD__HW_LOCK` commands with client, lock/release flag, hardware lock mask, and per-instance flags. `dmub_hw_lock_mgr_inbox0_cmd()` sends compact inbox0 lock commands and waits for ACK. Decision helpers are `dmub_hw_lock_mgr_does_link_require_lock()`, `dmub_hw_lock_mgr_does_context_require_lock()`, `should_use_dmub_inbox1_lock()`, and `should_use_dmub_inbox0_lock_for_link()`.

Control flow: link-level lock requirement returns true for PSR SU1, Replay on embedded signal, and PSR1 when there is exactly one eDP link. Context-level logic scans streams and delegates to the link helper. Inbox1 is used only when DMUB exists, DCN version is below 4.01, inbox0 lock support is absent, and the link requires a lock. Inbox0 is used when firmware metadata advertises `inbox0_lock_support` and the link requires the lock.

State and persistence: no long-lived state is held here. State is read from DC context, DMUB firmware metadata, link PSR/Replay settings, and command flags. Lock state persists in DMUB/hardware until released; unlock commands set `should_release`.

Dependencies and integration: depends on `dc_dmub_srv`, `core_types`, DMUB command unions, `dc_get_edp_links`, and DC hardware sequencing callbacks. It integrates with commit and power-feature paths that must interlock hardware programming with firmware autonomous PSR/Replay behavior.

Risks: incorrect feature detection can choose the wrong lock transport or skip a required lock, leading to races with firmware. Inbox0 support requires several function pointers and firmware metadata to be valid. Test signals include PSR1 single-eDP versus multi-eDP, PSR SU1, Replay embedded links, DCN 4.01 exclusion, inbox0 metadata presence, command release flag, and context scans with null contexts/links.
