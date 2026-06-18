# sources/distributed-fs/ceph/src/mon/OSDMonitor.cc lines 16119-16125

## Scope

This chunk is the tail of `OSDMonitor::trigger_healthy_stretch_mode()`. The function is called after stretch-mode recovery has completed, either because `try_end_recovery_stretch_mode()` observed no degraded, inactive, or unknown PG recovery state in `PGMapDigest`, or because the caller forced the transition. The covered lines update every stretch-aware pool in the pending OSDMap increment, then submit the increment with `propose_pending()`.

The exact covered operations are:

- Clear the pool's required CRUSH member with `peering_crush_mandatory_member = CRUSH_ITEM_NONE`.
- Restore the pool's `min_size` from monitor configuration `mon_stretch_pool_min_size`.
- Mark the pending epoch as `last_force_op_resend`.
- Close the loop and call `propose_pending()`.

The immediately preceding lines in the same function set `newp.peering_crush_bucket_count = osdmap.stretch_bucket_count` and reset the global stretch-mode fields in `pending_inc` so `degraded_stretch_mode` and `recovering_stretch_mode` become zero.

## Purpose

The purpose of this chunk is to finish returning a stretch-mode pool from a degraded single-site peering posture to the normal healthy stretch-mode posture. While degraded, `trigger_degraded_stretch_mode()` lowers each affected pool's `peering_crush_bucket_count` to the remaining site count, sets `peering_crush_mandatory_member` to the surviving site, halves `min_size`, and forces operation resend. This chunk reverses the pool-specific parts of that degraded-mode relaxation.

Clearing `peering_crush_mandatory_member` removes the requirement that PG acting sets include a replica under one specific CRUSH bucket. Restoring `min_size` to `mon_stretch_pool_min_size` reinstates the normal write/recovery availability threshold for stretch pools. Updating `last_force_op_resend` forces clients and OSD-side PG handling to discard or resend operations that were mapped against the older degraded/recovering pool parameters. `propose_pending()` then persists and publishes the OSDMap increment through the monitor proposal path.

## Important APIs, Types, and Fields

- `OSDMonitor::trigger_healthy_stretch_mode()` is a monitor-side transition helper. It asserts writeability before building a pending OSDMap increment and proposing it.
- `osdmap.pools` is the current pool map. The loop copies each pool entry by value as `pgi`; only pools with non-zero `peering_crush_bucket_count` are treated as stretch-aware pools.
- `pending_inc.get_new_pool(pgi.first, &pgi.second)` returns a mutable `pg_pool_t` entry in `OSDMap::Incremental::new_pools`, initialized from the current pool if needed.
- `pg_pool_t::peering_crush_mandatory_member` is an optional CRUSH item that stretch peering must include. `CRUSH_ITEM_NONE` disables the mandatory-member constraint.
- `pg_pool_t::min_size` is the minimum number of acting replicas needed for normal IO and recoverability decisions.
- `g_conf().get_val<uint64_t>("mon_stretch_pool_min_size")` supplies the configured healthy stretch pool minimum size used here and when enabling stretch mode.
- `pg_pool_t::set_last_force_op_resend(pending_inc.epoch)` sets `last_force_op_resend`, `last_force_op_resend_prenautilus`, and `last_force_op_resend_preluminous` to the pending OSDMap epoch for compatibility with older clients.
- `propose_pending()` submits the constructed `pending_inc` through monitor consensus, making the transition durable only after the proposal commits.

## Control Flow

`try_end_recovery_stretch_mode()` first ensures the monitor is leader, degraded stretch mode is active, recovering stretch mode is active, and the OSDMonitor plus MgrStatMonitor data are readable. It waits asynchronously with `CMonExitRecovery` if either monitor component is not readable. Once the configured `mon_stretch_recovery_min_wait` has elapsed, or the request is forced, it reads `PGMapDigest` recovery counters and calls `mon.trigger_healthy_stretch_mode()` if no degraded, inactive, or unknown PGs remain.

Inside `trigger_healthy_stretch_mode()`, the monitor resets the in-memory `stretch_recovery_triggered` timestamp, marks `pending_inc.change_stretch_mode`, copies the current stretch enablement, bucket count, and bucket type into the increment, and sets both `new_degraded_stretch_mode` and `new_recovering_stretch_mode` to zero. The loop in this chunk then applies the matching pool-level state restoration for pools that are already stretch-aware. Non-stretch pools are skipped because their `peering_crush_bucket_count` is zero.

The function ends with `propose_pending()`. There is no local return-value handling in this helper; success or retry is governed by the monitor proposal machinery.

## State and Persistence Behavior

The state changes are staged in `OSDMap::Incremental`, not written directly into the current committed `osdmap`. The global stretch-mode fields staged before the covered lines are applied by `OSDMap::apply_incremental()` when `inc.change_stretch_mode` is true: `stretch_mode_enabled`, `stretch_bucket_count`, `degraded_stretch_mode`, `recovering_stretch_mode`, and `stretch_mode_bucket` are copied from the increment.

The pool changes staged in `pending_inc.new_pools` are encoded as part of the same OSDMap epoch. After commit, each restored pool has no mandatory CRUSH member, has its stretch bucket count restored to the full stretch bucket count, and has `min_size` reset to the configured healthy stretch value. `last_force_op_resend` is persistent pool metadata; clients and OSD PG code use it as an epoch fence. For example, PG message handling rejects messages from epochs older than the pool's `last_force_op_resend`, and Objecter tracking observes this field to resend operations when the map epoch reaches the force-resend epoch.

`stretch_recovery_triggered` itself is local monitor state used to debounce recovery exit checks. It is cleared before the proposed map transition, but the durable cluster-visible change is the OSDMap increment.

## Dependencies and Integration Points

This chunk depends on the stretch-mode state prepared by nearby helpers:

- `trigger_degraded_stretch_mode()` enters degraded mode, constrains pools to the surviving CRUSH site, reduces `min_size`, and forces operation resend.
- `trigger_recovery_stretch_mode()` marks recovery mode and forces resend without changing pool placement constraints.
- `try_end_recovery_stretch_mode()` decides when this healthy transition is allowed using monitor leadership/readability, Mgr PG digest recovery stats, `mon_stretch_recovery_min_wait`, and optional force.
- `try_enable_stretch_mode()` initializes the same pool fields when stretch mode is first enabled.
- `try_disable_stretch_mode()` clears stretch-mode pool fields entirely when stretch mode is disabled, but refuses to run while recovering.

Downstream consumers include OSD peering code, client/Objecter map handling, and any monitor command/reporting path that dumps pool fields. `PeeringState` uses `peering_crush_mandatory_member` to ensure a selected acting set includes a required CRUSH ancestor when one is configured, and uses `min_size` to decide whether recovery and IO can proceed. OSDMap encoding/decoding persists these fields across monitor epochs and distributes them to OSDs and clients.

## Risks

- The function assumes it is called only while the monitor is writeable; the `ceph_assert(is_writeable())` catches violations but would crash in assert-enabled builds.
- Resetting `min_size` from `mon_stretch_pool_min_size` rather than the pool's previous value means operator changes made while degraded could be overwritten for stretch-aware pools during recovery exit.
- The loop selects pools by non-zero `peering_crush_bucket_count`. A pool with partially inconsistent stretch fields but zero bucket count would not be repaired by this transition.
- `pgi` is copied by value, so the function relies on `pending_inc.get_new_pool()` to update the real pending pool entry. This is correct here, but future edits must avoid mutating `pgi.second` directly.
- If `propose_pending()` fails, is delayed, or loses leadership before commit, the durable OSDMap transition has not happened even though local `stretch_recovery_triggered` was cleared.
- `set_last_force_op_resend()` intentionally perturbs client/OSD operation flow. Missing this call could leave operations mapped under degraded constraints in flight; setting it unnecessarily can cause extra client resend work.

## Test and Validation Signals

Useful coverage should exercise a two-site stretch cluster through degraded, recovery, and healthy transitions:

- Unit or integration tests should verify that exiting recovery sets `degraded_stretch_mode == 0`, `recovering_stretch_mode == 0`, preserves `stretch_mode_enabled`, and keeps `stretch_bucket_count` and `stretch_mode_bucket` aligned with the pre-existing stretch configuration.
- Pool assertions should check that each stretch-aware pool has `peering_crush_bucket_count == osdmap.stretch_bucket_count`, `peering_crush_mandatory_member == CRUSH_ITEM_NONE`, `min_size == mon_stretch_pool_min_size`, and `last_force_op_resend == pending epoch`.
- Recovery-gating tests should cover both natural exit after `mon_stretch_recovery_min_wait` with clean PG digest counters and forced exit with non-clean counters.
- Peering tests should confirm that acting-set selection no longer requires the formerly surviving CRUSH site after healthy transition and that the restored `min_size` is enforced.
- Client/Objecter or OSD PG tests should observe operation resend or rejection behavior around the `last_force_op_resend` epoch.
- Negative tests should verify `try_disable_stretch_mode()` remains blocked while recovering, and that non-stretch pools are not modified by `trigger_healthy_stretch_mode()`.
