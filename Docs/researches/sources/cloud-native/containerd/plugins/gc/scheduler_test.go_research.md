# sources/cloud-native/containerd/plugins/gc/scheduler_test.go

## Purpose
Unit tests the GC scheduler timing and trigger policy.

## Important APIs, Types, And Functions
Tests include `TestPauseThreshold`, `TestDeletionThreshold`, `TestTrigger`, and `TestStartupDelay`. `testCollector` implements mutation callbacks and `GarbageCollect`. `gcStats` supplies elapsed duration.

## Control Flow
Tests instantiate schedulers with controlled configs and collectors, run them in a goroutine using test contexts, trigger mutations or waits, sleep/select for expected scheduling, and assert run counts or elapsed stats.

## State And Persistence
All state is in-memory. The collector only increments counters and returns synthetic elapsed times.

## Dependencies And Integration Points
Uses `testing`, `sync`, `time`, `tomlext`, `pkg/gc`, and `testify/assert`. Directly targets `newScheduler`, `run`, `wait`, and callback behavior.

## Risks
Timing-sensitive sleeps can be flaky under very slow CI. Tests do not cover GC failure, mutation threshold behavior, context cancellation while waiting, or waiter notification ordering.

## Test Signals
Provides targeted confidence for core scheduling heuristics and manual synchronous GC.
