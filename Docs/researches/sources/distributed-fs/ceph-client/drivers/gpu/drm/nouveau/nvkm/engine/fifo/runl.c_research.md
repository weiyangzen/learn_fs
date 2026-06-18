# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.c

Purpose: implements generic FIFO runlist lifecycle, lookup, update gating, block/allow, and recovery-control logic shared by NV50+ and modern FIFO backends.

Important APIs and data: `nvkm_runl_new()`, `nvkm_runl_get()`, `nvkm_runl_add()`, `nvkm_runl_del()`, `nvkm_runl_fini()`, `nvkm_runl_block()`, `nvkm_runl_allow()`, `nvkm_runl_update_locked()`, `nvkm_runl_update_pending()`, `nvkm_runl_preempt_wait()`, `nvkm_runl_rc_engn()`, `nvkm_runl_rc_cgrp()`, `nvkm_runl_chan_get_chid()`, `nvkm_runl_chan_get_inst()`, and `nvkm_runl_cgrp_get_cgid()`.

Control flow: recovery starts when a channel group or engine schedules RC. The runlist is blocked, optionally preempted, `rc_pending` is incremented, and work is queued. The worker locks the runlist, marks pending channel groups as running recovery, errors and removes their channels, waits for runqueues to idle on preempt-capable hardware, resets engines still pointing at recovering groups, commits a runlist update, clears fault state, unblocks the runlist as many times as it was blocked for RC, and waits for the update.

State and persistence: state is runtime-only: runlist lists, engine list, cgrp/chan counts, `changed`, `blocked`, `rc_triggered`, `rc_pending`, runlist memory pointer/offset, work item, mutex, and shared `nvkm_chid` references. Lookup helpers return objects with locks held and irq flags handed back to callers.

Dependencies and integration: depends on channel/group/chid/runqueue structures, TOP fault-id lookup, engine reset, timers, and chip-specific `nvkm_runl_func` callbacks for update, wait, pending, block, allow, fault clear, and preempt.

Risks: recovery can reset engines and kill all channels in a group; lock ordering between CHID locks and group locks is critical; missing `cxid`/`idle` callbacks reduce recovery precision; block counters must remain balanced.

Test signals: runlist update after channel insert/remove, RC scheduling logs, errored-channel events, successful preempt wait, no deadlocks under concurrent channel destruction and interrupt recovery, and clean unload after `flush_work()`.
