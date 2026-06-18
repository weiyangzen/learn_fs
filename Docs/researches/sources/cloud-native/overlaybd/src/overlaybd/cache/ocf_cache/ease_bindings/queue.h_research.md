<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h

## Purpose
Declares the queue binding surface used to plug Photon execution into OCF queue operations.

## Important APIs, Types, And Functions
Exports `init_queues(ocf_queue_t mngt_queue, ocf_queue_t io_queue)` and `get_queue_ops()`.

## Control Flow
Provider startup obtains queue ops through this header, creates OCF queues, and then initializes their queue-private kickers.

## State And Persistence
The header owns no state. Queue-private state is implemented in `queue.cpp`.

## Dependencies And Integration Points
Includes the C OCF headers inside `extern "C"`, making the wrapper callable from C++ OCF binding code.

## Risks And Test Signals
The narrow API hides ownership details; callers must pair queue creation and provider cleanup correctly. Test signal is indirect cache initialization. Source size reviewed: 9 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/queue.h -->
