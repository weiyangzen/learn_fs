# sources/distributed-fs/ceph-client/include/media/media-request.h

## Purpose
Defines the media request API used to bundle controls, buffers, and driver objects into an atomic-ish queueable media operation.

## Important APIs, Types, and Functions
`enum media_request_state` covers idle, validating, queued, complete, cleaning, and updating. `struct media_request` stores owning media device, kref, debug string, state, updating/access counters, object list, incomplete count, manual completion flag, poll waitqueue, and spinlock. Request APIs include lock/unlock for access/update, get/put, get by fd, allocate, manual completion marking, and completion. `struct media_request_object_ops` supplies prepare/unprepare/queue/unbind/release. `struct media_request_object` stores object ops/private pointer/request/list/kref/completed state. Object APIs initialize, bind, find, unbind, complete, get, and put objects.

## Control Flow
Userspace allocates a request fd, drivers bind objects while the request is idle/updating, queueing validates and queues objects, and completion occurs when all bound objects complete or manual completion is explicitly called. Buffer objects are appended to the end of the object list so non-buffer dependencies queue first.

## State and Persistence Behavior
Request state is refcounted and protected by `req->lock`; access locks are allowed only after complete, update locks only while idle/updating. Object refs protect embedded objects after dropping the request lock. Incomplete object count gates poll/completion.

## Dependencies and Integration Points
Depends on media-device request ops, list/slab/spinlock/refcount infrastructure, vb2 buffer request integration, and media-controller configuration.

## Risks
Incorrect state transitions return `-EBUSY` or can deadlock request updates. Failing to complete or unbind every object leaves requests permanently incomplete. Calling manual completion before all objects complete triggers warnings and delayed completion. Disabled media-controller stubs change behavior to errors/no-ops.

## Test Signals
Request fd allocation/get/put, update/access lock rejection in wrong states, object bind ordering, prepare/unprepare failure unwinds, queue callback ordering with vb2 buffers last, poll completion, manual completion, object find refcounts, and disabled-config builds.
