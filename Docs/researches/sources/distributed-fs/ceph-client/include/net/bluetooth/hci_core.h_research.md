# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_core.h

## Purpose

`hci_core.h` defines the Bluetooth HCI core object model and internal APIs: devices, connections, channels, discovery cache, keys, advertising instances, monitoring, command queues, management hooks, capability macros, protocol callbacks, and socket/monitor send paths.

## Important APIs, Types, and Functions

Core data types include `struct hci_dev`, `struct hci_conn`, `struct hci_chan`, `struct hci_conn_params`, discovery/inquiry entries, security key lists (`link_key`, `smp_ltk`, `smp_irk`, `smp_csrk`, blocked keys, OOB data), advertising instances, advertising monitors, codec lists, and connection hash counters. `struct hci_dev` is the large per-controller state object: identity addresses, features, command masks, defaults, buffers and MTUs, workqueues, command/sync queues, rx/raw/cmd queues, request wait state, discovery/suspend/advertising/privacy state, connection hash, key/accept/resolving lists, stats, devcoredump, rfkill, debugfs, driver callbacks, and optional MSFT/AOSP/LED data.

Inline helpers initialize/clear discovery filters, add/delete/list RCU connection hash entries, lookup connections by handle/address/role/ISO identifiers/PA/BIG state, manage device and connection references, schedule delayed disconnects when connection holds drop, dispatch connect/disconnect/security/key/role callbacks, classify RPAs and identity addresses, validate LE connection parameters, and map HCI link types to L2CAP/SCO/ISO protocol indications. Exported prototypes cover device allocation/registration/open/close/reset, frame receive, ioctls, inquiry cache, key and address-list management, connection creation/security/PHY/update/abort, advertising instances and monitors, HCI command/data send, management channel registration, sysfs, and MGMT event reporting.

## Control Flow

Driver probe allocates and fills `hci_dev`, sets quirks/callbacks, and registers it. Open/setup populates command masks, features, addresses, MTUs, keys, advertising defaults, and scan parameters, usually through synchronous command helpers. Incoming transport frames enter `hci_recv_frame()` and are dispatched by packet type to event, ACL, SCO, or ISO handling. Event handling updates device/connection state, completes commands, updates discovery cache, resolves security transitions, and calls upper protocol indications. Connection creation uses the hash/list helpers, delayed works for timeouts/idle/disconnect, and protocol callbacks into L2CAP/SCO/ISO. Management sockets observe settings, discovery, pairing, key, advertising, suspend, and monitor events through the many `mgmt_*` hooks.

## State and Persistence Behavior

All state is in kernel memory attached to the HCI device, connection devices, queues, lists, delayed work, and registered callbacks. Link keys, LTKs, IRKs, OOB data, connection parameters, and advertising instances are represented in memory here and may be persisted by userspace management policy, but this header itself provides only runtime containers and notifications. RCU protects connection hash and key-like lists; device/connection lifetimes use `struct device` refs plus separate connection hold counts.

## Dependencies and Integration Points

The header depends on IDR/IDA, LEDs, RCU/SRCU, spinlocks, mutexes, workqueues, rfkill, sk_buffs, `hci.h`, driver command extensions, sync command helpers, HCI sockets, and devcoredump. It integrates with Bluetooth drivers, HCI sockets, MGMT, L2CAP, SCO, ISO, sysfs, debugfs, rfkill, suspend notifiers, and optional MSFT/AOSP extensions.

## Risks and Edge Cases

Several inline lookup helpers return pointers found under RCU after dropping the read lock; callers must ensure object lifetime through surrounding locking/ref rules. The comment around `hci_conn_get()` versus `hci_conn_hold()` documents a subtle split between object lifetime and physical connection lifetime, including a FIXME about hold counts dropping below zero. Many capability macros trust command/feature array offsets. Workqueue cancellation during unregister, suspend, and close is high risk. LE/ISO lookup helpers must distinguish listen, pending, PA, BIS, CIG, and BIG states correctly. Connection parameter validation prevents invalid controller commands but must remain aligned with Bluetooth timing rules.

## Test Signals

Test device register/open/setup/close/unregister, receive dispatch for event/ACL/SCO/ISO/diag, command timeout and sync cancellation, connection hash add/delete/lookups under RCU, key/IRK/LTK/OOB list add/remove/clear, LE connection parameter validation, discovery cache aging/filtering/name resolution, advertising instance and monitor lifecycle, suspend/resume notifier states, rfkill, devcoredump setup, management notifications, and disabled SCO/ISO configurations.
