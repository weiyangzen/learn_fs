<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp

## Purpose
Implements OCF queue callbacks by mapping OCF queue kicks onto Photon threads or Photon work pools.

## Important APIs, Types, And Functions
Defines `QueueKicker`, `init_queues`, `queue_thread_kick`, `queue_thread_stop`, static `queue_ops`, and `get_queue_ops`.

## Control Flow
OCF calls the queue ops `kick`; the private `QueueKicker` runs `ocf_queue_run` either through a configured `photon::WorkPool` or a newly created Photon thread. `init_queues` installs one management kicker and one IO kicker, with different worker counts and Photon event/IO engines. The stop callback deletes the kicker stored in OCF queue private data.

## State And Persistence
State is transient queue-private `QueueKicker` objects. There is no durable state; queue lifetimes must match OCF cache/provider lifetimes.

## Dependencies And Integration Points
Depends on OCF queue APIs and Photon thread/workpool initialization constants. It is called from `ease_ocf_provider::start` after OCF queue creation.

## Risks And Test Signals
`QueueKicker::kick` captures `this` in a heap-allocated lambda for async work; stop must not race with queued callbacks. WorkPool initialization choices couple OCF IO to libcurl/epoll. Coverage is indirect through OCF cache startup and `ocf_perf_test`; source size reviewed: 70 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.cpp -->
