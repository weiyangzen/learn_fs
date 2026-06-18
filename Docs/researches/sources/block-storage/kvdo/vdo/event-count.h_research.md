# File Research: sources/block-storage/kvdo/vdo/event-count.h

## Purpose
Declares the opaque event-count synchronization primitive.

## API
- `make_event_count()` / `free_event_count()`
- `event_count_broadcast()`
- `event_count_prepare()`
- `event_count_cancel()`
- `event_count_wait()`

## Usage Contract
Callers prepare a token, re-check their condition, then either cancel the token or wait on it. A timeout pointer is optional and measured as a `ktime_t`.
