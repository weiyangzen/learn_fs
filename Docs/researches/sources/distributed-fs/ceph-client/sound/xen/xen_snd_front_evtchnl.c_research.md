# sources/distributed-fs/ceph-client/sound/xen/xen_snd_front_evtchnl.c

## Purpose
Allocates, publishes, handles, and frees Xen event channels and shared rings for each Xen sound stream. It provides one request/response channel and one async event channel per stream.

## Important APIs, Types, And Functions
- `evtchnl_interrupt_req()` consumes backend responses from a Xen ring, matches the current request id, stores status/response payload, and completes waiters.
- `evtchnl_interrupt_evt()` consumes async events from the event page and dispatches current-position updates to ALSA.
- `xen_snd_front_evtchnl_flush()` pushes one request and notifies the backend.
- `evtchnl_alloc()` sets up a grant-backed page, event channel port, IRQ binding, and threaded IRQ handler.
- `xen_snd_front_evtchnl_create_all()` allocates request/event pairs for every configured stream.
- `xen_snd_front_evtchnl_publish_all()` writes ring refs and event-channel ports to XenStore in a transaction.
- `xen_snd_front_evtchnl_pair_set_connected()` and `xen_snd_front_evtchnl_pair_clear()` manage stream connection and event ids.

## Control Flow
During frontend InitWait, `create_all()` allocates all channel pairs following configured stream indices. `publish_all()` transactionally writes request ring ref/port and event ring ref/port under each stream's XenStore path. Stream operations fill request slots and call `flush()`. Request IRQs drain responses, use memory barriers around producer indexes, and complete the synchronous waiter. Async event IRQs drain event-page entries, enforce monotonically expected ids, and pass current-position events to ALSA.

## State And Persistence
Each channel stores grant ref, event port, IRQ, index, state, type, current/next event ids, ring lock, and union-specific request or event-page state. Channel state is transient; XenStore-published refs/ports advertise it to the backend until freed or backend resets.

## Dependencies And Integration Points
Depends on Xen event, grant-table, XenBus ring setup/teardown, Xen sound protocol definitions, parsed config, and ALSA current-position handling. It is called by `xen_snd_front.c` for lifecycle and by stream operations for request flushing.

## Risks
- The code trusts backend ring counters and event ids enough to avoid overflow validation.
- `evtchnl_alloc()` fail paths return after partial setup; caller frees all pairs, but individual partial resources must be initialized consistently.
- Request matching ignores responses with unexpected ids, so a lost/mismatched response can cause timeout.
- Async current-position events require `substream` to be valid while channel is connected.
- Transaction publish retries only on `-EAGAIN`; other failures call `xenbus_dev_fatal()`.

## Test Signals
Test allocation failure at ring, event-channel, IRQ bind, and request IRQ stages; XenStore transaction retry; backend response id mismatch; current-position event id gaps; disconnect while a request waits; and backend reset with all resources freed.
