# sources/distributed-fs/ceph-client/samples/watch_queue/watch_test.c

## Purpose
`watch_test.c` demonstrates the watch queue notification API by watching keyring change notifications through an `O_NOTIFICATION_PIPE`.

## APIs, Types, And Functions
Important APIs are `pipe2(O_NOTIFICATION_PIPE)`, `IOC_WATCH_QUEUE_SET_SIZE`, `IOC_WATCH_QUEUE_SET_FILTER`, and `keyctl(KEYCTL_WATCH_KEY, ...)`. `consumer()` reads and decodes notification records, while `saw_key_change()` formats `struct key_notification` messages.

## Control Flow
`main()` creates a notification pipe, sizes the watch queue, installs a filter for key notifications, attaches watches for the session and user keyrings, then calls `consumer()`. The consumer reads batches, iterates variable-length `watch_notification` records, validates record lengths, and switches on meta versus key notification types.

## State And Persistence
State is limited to pipe fds, installed watches, filter structure, and the read buffer. Watches persist only while the process/fds remain alive.

## Dependencies And Integration Points
It depends on watch queue UAPI, keyctl syscall support, keyring constants, and the kernel key retention service. It integrates with keyring update events and watch meta notifications for removal/loss.

## Risks And Test Signals
Risks include unsupported watch queues, permission failures for key watches, malformed/short records, and fixed buffer assumptions. Test signals are printed notifications after keyring operations, meta loss/removal handling, and clean read-loop behavior when the pipe closes.
