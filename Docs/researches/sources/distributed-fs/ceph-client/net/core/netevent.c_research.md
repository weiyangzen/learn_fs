<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netevent.c -->
# sources/distributed-fs/ceph-client/net/core/netevent.c

## Purpose
Small exported notifier-chain wrapper for network events, historically used by neighbor and related networking subsystems to publish asynchronous events to registered listeners.

## APIs, Types, and Functions
The file owns `ATOMIC_NOTIFIER_HEAD(netevent_notif_chain)` and exports `register_netevent_notifier()`, `unregister_netevent_notifier()`, and `call_netevent_notifiers()`.

## Control Flow, State, and Persistence
Registered `notifier_block` instances persist in the atomic notifier chain until unregistered. `call_netevent_notifiers()` forwards the event value and opaque pointer through `atomic_notifier_call_chain()` without interpreting them.

## Dependencies and Integration
Depends on Linux notifier infrastructure and is included through `net/netevent.h`. It is suitable for contexts that require atomic notifier semantics rather than blocking notifier semantics.

## Risks and Test Signals
Risks are mostly consumer-side: notifier blocks must not be reused while registered, callbacks must tolerate atomic context, and event payload typing is implicit. Test signals are registration/unregistration return codes, callback ordering/counts, and safe behavior when no listeners exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netevent.c -->
