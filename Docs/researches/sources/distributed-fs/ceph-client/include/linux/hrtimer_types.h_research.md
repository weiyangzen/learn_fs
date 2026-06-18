# sources/distributed-fs/ceph-client/include/linux/hrtimer_types.h

## Purpose
`hrtimer_types.h` defines the basic hrtimer object and callback return values, separated from the larger hrtimer API to reduce include coupling.

## Important APIs, Types, And Functions
`enum hrtimer_restart` has `HRTIMER_NORESTART` and `HRTIMER_RESTART` callback outcomes. `struct hrtimer` contains a timerqueue node with expiry, a clock-base pointer, flags for queued/relative/soft/hard/lazy state, `_softexpires`, and the private callback function pointer.

## Control Flow And State
Hrtimer code initializes this structure, inserts `node` into a timerqueue, sets `base`, tracks queued state, records mode-derived flags, and invokes `function` when expired. Callback return controls whether the timer is rearmed. `_softexpires` is the earliest expiry while `node.expires` may include slack.

## Dependencies And Integration Points
It depends on basic types and timerqueue types. It integrates with `hrtimer_defs.h` per-CPU bases and `hrtimer.h` public operations.

## Risks
Risks include direct field manipulation by callers instead of using APIs, callback pointer update while queued, confusing hard and soft expiry, and stale `base` assumptions after migration. The callback is marked `__private`, signaling callers should use provided helpers.

## Test Signals
Build all hrtimer users, run callback restart/no-restart tests, slack/range timer tests, migration/cancel tests, and compile checks that discourage direct private callback access.
