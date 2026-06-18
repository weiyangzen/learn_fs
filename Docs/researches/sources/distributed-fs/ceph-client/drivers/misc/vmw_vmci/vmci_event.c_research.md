# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.c

Purpose: implements in-kernel VMCI event subscription and dispatch for hypervisor/context/queue-pair events.

Important APIs/functions: `vmci_event_init()` initializes per-event subscriber lists. `vmci_event_exit()` frees remaining subscribers with warnings. `vmci_event_dispatch()` validates event datagram payload size and event number, then calls `event_deliver()`. `vmci_event_subscribe()` allocates a subscription, generates a nonduplicate ID with limited attempts, and links it under RCU. `vmci_event_unsubscribe()` removes by subscription ID and frees via RCU.

Control flow: event datagrams are delivered from guest interrupt handling or local host-generated event paths. Delivery sanitizes the event index with `array_index_nospec()`, enters an RCU read-side section, iterates the selected subscriber list, and invokes callbacks. Subscription mutation is serialized by `subscriber_mutex`.

State/persistence: static `subscriber_array[VMCI_EVENT_MAX]` stores volatile subscriptions. Subscription IDs come from a static incrementing counter inside subscribe.

Dependencies/integration: used by guest CID update subscription, queue-pair peer attach/detach notifications, context removal events, and datagram dispatch of hypervisor event messages.

Risks: callback functions run inside RCU read-side critical section and must not sleep. `vmci_event_subscribe()` writes `*new_subscription_id = sub->id` even on failure, and currently leaks `sub` when no ID is found because the failure path does not free it. Event ID generation only attempts `VMCI_EVENT_MAX_ATTEMPTS`.

Test signals: invalid event payload sizes, invalid event numbers, subscribe/unsubscribe races with dispatch, callback non-sleeping expectations, duplicate ID exhaustion, and module exit with lingering subscriptions.
