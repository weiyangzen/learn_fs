# sources/distributed-fs/ceph-client/net/bluetooth/coredump.c

## Purpose
This file implements the Bluetooth HCI devcoredump state machine used by drivers to collect controller/firmware dumps, mirror them to HCI diagnostics, and publish them through the kernel devcoredump facility.

## Important APIs, Types, And Functions
Exported APIs are `hci_devcd_register()`, `hci_devcd_init()`, `hci_devcd_append()`, `hci_devcd_append_pattern()`, `hci_devcd_complete()`, `hci_devcd_abort()`, `hci_devcd_rx()`, and `hci_devcd_timeout()`. Internal helpers allocate/copy/memset dump buffers, build headers, update state, notify drivers, emit dumps, and reset/free state.

## Control Flow
Drivers register coredump, header, and optional notification callbacks. Public append/init/complete/abort APIs package requests as typed skbs on `hdev->dump.dump_q` and queue `dump_rx` work. The worker processes packets sequentially under `hci_dev_lock()`: INIT allocates a vmalloc buffer containing the generic and driver header, switches to ACTIVE, and starts a timeout; SKB and PATTERN append data while ACTIVE; COMPLETE and ABORT switch to terminal states and emit a dump. After terminal states, the worker notifies state changes and resets the state machine. Timeout work notifies the driver, cancels pending RX work, marks TIMEOUT, emits available data, resets, and unlocks.

## State, Persistence, And Dependencies
State is stored in `hdev->dump`: head/tail/end pointers, allocation size, current state, work items, skb queue, timeout, callbacks, and support flag. Dump memory is vmalloc'd per active dump and handed to `dev_coredumpv()`, transferring ownership to the devcoredump core. Runtime state is not persisted by this module.

## Integration Points
Bluetooth HCI drivers call the exported APIs. The file integrates with `linux/devcoredump.h`, HCI diagnostic receive (`hci_recv_diag()`), HCI workqueues, device logging, skb queues, unaligned little-endian helpers, and optional driver callbacks.

## Risks
The state machine is strict; packets in unexpected states are logged and ignored, so driver ordering bugs can lose dump data. Size accounting prevents writes past the allocated buffer, but failed append attempts only log debug messages. Timeout cancels RX work while queued skbs may remain until reset purges the queue. Header size is capped at 512 bytes, so oversized driver headers can overflow the temporary skb if not controlled by driver callback behavior.

## Test Signals
Signals include successful init/append/complete producing a devcoredump and diagnostic skb, abort producing a partial dump, timeout producing a partial dump and notifying the driver, pattern append filling expected bytes, invalid state transitions not crashing, and reset freeing/purging all dump resources.
