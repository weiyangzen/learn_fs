# sources/distributed-fs/ceph-client/include/net/bluetooth/coredump.h

## Purpose

`coredump.h` defines Bluetooth HCI device firmware/controller devcoredump state and the optional APIs drivers use to collect, append, complete, abort, and time out dumps.

## Important APIs, Types, and Functions

`struct hci_devcoredump` tracks support, state (`IDLE`, `ACTIVE`, `DONE`, `ABORT`, `TIMEOUT`), timeout, allocated dump buffer pointers, skb dump queue, work items, and driver callbacks for triggering dump collection, building a dump header, and notifying state changes. With `CONFIG_DEV_COREDUMP`, exported functions include reset, RX work, timeout work, register, init allocation, append skb, append repeated pattern, complete, and abort. Without devcoredump support, inline stubs return `-EOPNOTSUPP` or no-op.

## Control Flow

Drivers register callbacks, initialize a dump buffer, append dump fragments into the buffer via queued skb processing, and call complete or abort. Timeout work transitions a stuck collection to timeout. State-change notifications let drivers synchronize firmware dump mode with the core.

## State and Persistence Behavior

Dump state is per `hci_dev` in memory. The final devcoredump may be exposed through the kernel devcoredump mechanism, but this header stores only transient collection buffers and workqueue state. Timeout defaults to ten seconds.

## Dependencies and Integration Points

The header depends on HCI device definitions, sk_buffs, workqueues, delayed work, and `CONFIG_DEV_COREDUMP`. It integrates with Bluetooth HCI drivers and the generic devcoredump subsystem.

## Risks and Edge Cases

Buffer pointer arithmetic (`head`, `tail`, `end`) must remain bounded by `alloc_size`. Dump fragments arriving after abort/timeout need safe rejection. Drivers must handle `-EOPNOTSUPP` when devcoredump is disabled. Work cancellation during device unregister is critical to avoid accessing freed `hci_dev`.

## Test Signals

Test successful dump registration/init/append/complete, append overflow, append pattern lengths, abort during active collection, timeout path, reset after completion, unregister with pending dump work, and disabled-configuration stubs.
