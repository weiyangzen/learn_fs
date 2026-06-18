# sources/distributed-fs/lustre-release/lnet/selftest/timer.c

## Purpose
Implements the selftest timer facility used for session expiry, console pinger scheduling, and client RPC timeouts.

## Important APIs And Functions
`stt_data` stores global timer state. Public functions are `stt_add_timer()`, `stt_del_timer()`, `stt_startup()`, and `stt_shutdown()`. Internal helpers include `stt_expire_list()`, `stt_check_timers()`, `stt_timer_main()`, and `stt_start_timer_thread()`.

## Control Flow
Timers are slotted into 8-second buckets across 128 slots, sorted within each slot. The `st_timer` thread periodically checks due slots, removes expired timers, unlocks, runs callbacks, and relocks. Shutdown asserts all timer lists are empty, sets the shutdown flag, wakes the thread, and waits for it to exit.

## State And Persistence
State is global kernel memory and caller-owned intrusive timer nodes. No persistence exists.

## Dependencies And Integration Points
Uses `stt_timer` from `timer.h`, kernel kthreads/wait queues/spinlocks, libcfs time helpers, and `lst_wait_until()` from `selftest.h`.

## Risks
Timer resolution is coarse, slot coverage wraps after roughly 1024 seconds, and `stt_del_timer()` returning zero can mean inactive or callback-running. Shutdown fails assertions if callers leave timers queued.

## Test Signals
Ordered expiry, deletion before expiry, callback-running race, integration with RPC/session timeout, and shutdown after all timers are removed.
