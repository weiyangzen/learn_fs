# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_delay.c

## Purpose

`nrs_delay.c` implements an NRS policy that deliberately delays a configurable percentage of PTLRPC requests for a random interval between configurable minimum and maximum seconds. It is useful for testing, fault injection, and controlled scheduling delay experiments rather than normal fairness scheduling.

## Important APIs, Types, and Functions

The policy state is `struct nrs_delay_data`, which holds a binheap, embedded resource, `min_delay`, `max_delay`, and `delay_pct`. Main hooks are `nrs_delay_start`, `nrs_delay_stop`, `nrs_delay_ctl`, `nrs_delay_res_get`, `nrs_delay_req_get`, `nrs_delay_req_add`, `nrs_delay_req_del`, and `nrs_delay_req_stop`. `delay_req_compare` sorts heap nodes by `nr_u.delay.req_start_time`. The exported configuration is `nrs_conf_delay`.

Debugfs files are created by `nrs_delay_lprocfs_init`: `nrs_delay_min`, `nrs_delay_max`, and `nrs_delay_pct`. Shared parsing is handled by `lprocfs_nrs_delay_seq_write_common`, and each setting has regular and HP queue-specific read/write handlers.

## Control Flow

Starting allocates `nrs_delay_data`, creates an atomic-grow binheap, and initializes defaults: minimum 5 seconds, maximum 300 seconds, and 100 percent delayed. Resource acquisition is one-level and returns the embedded delay resource.

On enqueue, the policy first decides whether this request should be handled by delay. If `delay_pct` is zero, or a random draw is outside the configured percentage, `nrs_delay_req_add` returns 1 so NRS core falls back to another policy. If selected, it computes `req_start_time` as current real seconds plus a random value in `[min_delay, max_delay]` and inserts the request into the heap. Dispatch returns the earliest request only after its start time has passed, unless core calls with `force` to drain a stopped policy. Dequeue removes the heap node. Stop asserts the heap is empty before destroying it.

Control operations read and write min, max, and percentage under the NRS lock. Writes enforce `min <= max`, `max >= min`, and percentage within 0 to 100. Debugfs writes accept `reg_delay_*:`, `hp_delay_*:`, or a bare numeric value, then apply through `ptlrpc_nrs_policy_control`.

## State and Persistence Behavior

The delay heap and settings are runtime-only per policy instance. There is no disk persistence. Existing queued requests retain their already assigned `req_start_time` when min, max, or percentage changes; new values affect later enqueues only.

## Dependencies and Integration Points

The file depends on NRS core hooks, Linux random (`get_random_u32_below`), real-time seconds (`ktime_get_real_seconds`), Lustre binheap utilities, debugfs/lprocfs helpers, PTLRPC request arrival timestamps for logging, and service regular/HP queue control. It is compatible with all PTLRPC services.

## Risks and Edge Cases

`delay_pct` is an unsigned value but the control code still checks `< 0`, which is ineffective but harmless. If `max_delay - min_delay + 1` is large, the random range calculation must remain within type bounds. Since the heap is ordered by wall-clock real seconds, system time changes can affect observed delay. A high delay percentage with long maximum delay can cause service backlog and apparent hangs unless operators understand the policy is active. Stopped-policy draining relies on `force` to return requests before their scheduled start time.

## Test Signals

Tests should cover delay selection at 0, partial, and 100 percent; random start times within inclusive bounds; heap ordering by earliest start time; `peek` preserving heap membership; `force` returning not-yet-ready requests; dequeue and stop with empty heap; debugfs parsing for regular, HP, and bare settings; min greater than max and max less than min rejection; percentage bounds; and runtime changes affecting only subsequent requests.
