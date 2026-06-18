# sources/cloud-native/moby/daemon/logger/loggerutils/queue.go

Purpose: blocking bounded queue for `logger.Message` pointers.

Important APIs/types/functions: `MessageQueue`, `NewMessageQueue`, `Enqueue`, `Close`, `Receiver`, and `ErrQueueClosed`.

Control flow/state/persistence: queue lazily initializes its channel/cond. `Enqueue` increments a sender waiter count, checks context and closed channel, then sends or returns cancellation/closed errors. `Close` closes the closed signal, waits for active senders via cond, closes the message channel, and lets receivers drain buffered entries.

Dependencies/integration: used by logging components that need bounded backpressure.

Risks: close/send coordination is subtle; callers remain responsible for returning undelivered messages to the pool when enqueue fails.

Test signals: `queue_test.go` covers enqueue, blocking, close, drain, and cancellation semantics.
