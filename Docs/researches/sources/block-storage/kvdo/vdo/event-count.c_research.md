# File Research: sources/block-storage/kvdo/vdo/event-count.c

## Purpose
Implements an event count: a lock-free condition-variable-like primitive for producer/consumer structures.

## Main Design
- `state` is an atomic 64-bit value split into low 16-bit waiter count and high 48-bit event counter.
- `event_count_prepare()` issues a token by incrementing waiter count.
- `event_count_broadcast()` increments the event counter, claims current waiters, and posts one semaphore token per waiter.
- `event_count_cancel()` tries to remove an unconsumed waiter token; if already signaled, it consumes the semaphore token instead.
- `event_count_wait()` consumes a token and returns when the event counter differs from the token, optionally timing out and cancelling if possible.

## Dependencies
Uses Linux atomics, UDS semaphore wrappers, scheduler yield, memory barriers, allocation, and cache-line alignment.

## Invariants
Every prepared token must be consumed by exactly one wait or cancel call. Tokens should only be held briefly; long delays before wait/cancel hurt performance and can increase contention.
