<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h

## Purpose
Private virtio-snd control-message API declaration shared by card, config parser, PCM, and kcontrol code.

## APIs, Types, and Functions
Forward-declares `struct virtio_snd` and `struct virtio_snd_msg`; declares ref/unref, request/response accessors, allocation, generic send, sync/async inline send wrappers, cancellation, completion, query-info, and control-virtqueue notification callback.

## Control Flow, State, and Persistence
The header has no state. The sync wrapper sends without extra scatterlists and waits; the async wrapper sends without waiting. Callers must honor the documented ownership rule that messages are normally freed when the final reference drops after completion.

## Dependencies and Integration
Includes Linux atomic and virtio types. Implemented by `virtio_ctl_msg.c` and included by `virtio_card.h`, making it visible throughout the virtio-snd driver.

## Risks and Test Signals
Risks include callers retaining message payloads without taking a reference, using sync sends from atomic context, or expecting async messages to outlive completion. Build coverage and runtime tests of parser queries, control reads/writes, and teardown cancellation validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.h -->
