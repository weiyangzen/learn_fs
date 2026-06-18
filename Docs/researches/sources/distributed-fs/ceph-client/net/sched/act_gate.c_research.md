# sources/distributed-fs/ceph-client/net/sched/act_gate.c

Purpose: implements the `gate` TC action, allowing packets only during configured time slots and optionally enforcing per-entry byte limits.

Important APIs/functions: `tcf_gate_init()` parses schedule parameters and starts the timer; `tcf_gate_act()` enforces current gate state; `gate_timer_func()` advances schedule entries; `parse_gate_list()`/`parse_gate_entry()` build entry lists; `tcf_gate_dump()` reports schedule; `tcf_gate_cleanup()` cancels timers and frees params; `tcf_gate_offload_act_setup()` maps schedules to `FLOW_ACTION_GATE`.

Control flow: init parses base time, cycle time, clock ID, flags, priority, and entry list. Replacement can reuse old entries and defaults. It resolves clock IDs to timekeeper offsets, cancels/reinitializes the hrtimer when timing base changes, computes cycle time from entries if omitted, RCU-swaps params, marks gate pending/open, selects the first entry, and starts the soft hrtimer at the next cycle boundary. The timer sets open/closed status, max octets, close time, advances to the next entry, and restarts. Runtime drops packets when pending is clear but gate is closed, or when byte count exceeds max octets; otherwise it returns the configured action.

State and persistence: per-action state includes RCU schedule params, an hrtimer, current/next entry pointers, current close time, gate status flags, octet counters, clock offset, stats, and goto-chain pointer. Schedule state is runtime-only.

Dependencies and integration: TC action API, hrtimer/timekeeping offsets, netlink nested attributes, qdisc packet length, flow offload gate entries, RCU cleanup, and pernet registration.

Risks: timer and action path share mutable gate state under `tcf_lock`; replacements must cancel timers when clock/base changes to avoid stale callbacks. Empty entry lists are invalid for new actions. Time arithmetic depends on nonzero cycle time and valid intervals. Offload entry duplication allocates memory that must be destroyed through the flow action entry destructor.

Test signals: open/closed slot behavior, max-octet drops/overlimits, base time in past/future, clock ID validation, replacement reusing entries, timer cancellation on timing changes, dump roundtrip, offload gate entry creation/destruction, and cleanup under active timer load.
