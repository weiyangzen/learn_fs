# sources/distributed-fs/ceph-client/rust/helpers/time.c

## Purpose
Exposes sleep/delay and ktime helpers to Rust.

## APIs, Types, and Functions
APIs include `fsleep`, `ktime_get_real`, `ktime_get_boottime`, `ktime_get_clocktai`, `ktime_to_us`, `ktime_to_ms`, and `udelay`.

## Control Flow, State, and Persistence
No local state; reads kernel clocks or busy/sleep delays according to wrapped APIs.

## Dependencies and Integration
Depends on `linux/delay.h`, `linux/ktime.h`, `linux/timekeeping.h`, and Rust time abstractions.

## Risks and Test Signals
Risks include using busy delay for long periods, sleeping in atomic context via `fsleep`, and clock-domain confusion. Test signals are Rust time conversion tests and context-sensitive delay tests.
