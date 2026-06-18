# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_pingpong.c

## Purpose
Implements a simple NTB ping-pong client that exercises link events, doorbells, scratchpads, and message registers. It selects an active peer, periodically writes a counter to peer scratchpad/message register, rings a peer doorbell, and counts received responses.

## Important APIs, Types, And Functions
- `struct pp_ctx` stores NTB device, timer, inbound/outbound doorbell masks, selected peer, peer masks, count, lock, and debugfs dir.
- `pp_check_ntb()` validates doorbell safety, scratchpad/message availability, and doorbell bit layout.
- `pp_find_next_peer()` selects a linked peer, preferring next peers then previous peers.
- `pp_ping()` writes counter to peer scratchpad/message and rings peer DB.
- `pp_pong()` reads received scratchpad/message values, increments count, clears/remasks inbound DB, and restarts timer.
- `pp_setup()` and `pp_clear()` arm/cancel the timer and mask DBs.

## Control Flow
Probe validates the NTB device, allocates context, computes local inbound DB and peer masks, masks events, sets NTB callbacks, enables link, triggers a link event, and creates debugfs. On link events, setup masks inbound DB, selects a linked peer, and starts a timer. Timer expiry sends a ping. Doorbell events call `pp_pong()`, which observes received data, increments the counter, clears/masks DB state, and schedules the next ping.

## State And Persistence
Only volatile kernel state is used. The peer-visible counter is stored transiently in scratchpad/message registers. Debugfs exposes `count`. Module parameters are `unsafe` and `delay_ms`.

## Dependencies And Integration Points
Depends on NTB link, doorbell, scratchpad, optional message APIs, hrtimer, debugfs, and atomic counters. It is a quick provider sanity test rather than a data transport.

## Risks And Edge Cases
- Uses port numbers as doorbell bit numbers; hardware must expose a matching valid mask.
- Message and scratchpad values can differ because message status must be cleared before rewriting.
- If all peers are down, setup cancels the ping-pong loop.
- `unsafe=1` is required to run on providers marking DB/SPAD unsafe; otherwise probe fails.

## Test Signals
`/sys/kernel/debug/ntb_pingpong/<dev>/count` should increase while both peers are loaded and linked. Link drops should stop and link returns should resume. Debug logs should show ping/pong counter values and selected peer ports.
