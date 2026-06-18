# sources/distributed-fs/ceph-client/net/bluetooth/af_bluetooth.c

## Purpose
This file implements the PF_BLUETOOTH address-family core: protocol registration, socket allocation and common socket helpers, accept-queue handling, shared recv/poll/ioctl/wait utilities, procfs socket listing, debugfs root creation, and subsystem init/exit orchestration.

## Important APIs, Types, And Functions
Exported protocol APIs include `bt_sock_register()`, `bt_sock_unregister()`, `bt_sock_alloc()`, `bt_sock_link()`, `bt_sock_unlink()`, `bt_sock_linked()`, `bt_accept_enqueue()`, `bt_accept_unlink()`, `bt_accept_dequeue()`, `bt_sock_recvmsg()`, `bt_sock_stream_recvmsg()`, `bt_sock_poll()`, `bt_sock_ioctl()`, `bt_sock_wait_state()`, `bt_sock_wait_ready()`, `bt_procfs_init()`, and `bt_procfs_cleanup()`. `bt_init()` registers the address family and initializes HCI sockets, L2CAP, SCO, and management; `bt_exit()` unwinds them and removes debugfs/sysfs/LED resources.

## Control Flow
`bt_sock_create()` validates init_net and protocol number, autoloads `bt-proto-%d` if needed, pins the protocol module, calls its create callback, and reclassifies socket locks for lockdep. Accept-queue helpers hold socket references, copy peer credentials from parent sockets, and safely dequeue connected or deferred-setup children. Datagram and stream recv helpers consume skb queues with truncation, ancillary HCI status/sequence cmsgs, MSG_PEEK support, and blocking waits. Poll combines state, shutdown, queue, error, suspend, and writeability conditions. Init follows selftest, debugfs, LEDs, sysfs, address-family registration, HCI socket, L2CAP, SCO, and management setup with reverse cleanup labels.

## State, Persistence, And Dependencies
The core protocol table `bt_proto[]` is protected by `bt_proto_lock`. Per-protocol lock-class arrays make lockdep distinguish Bluetooth protocols. Socket lists are maintained by protocol modules using `bt_sock_list`. `bt_debugfs` is an exported root dentry. Runtime state is in sockets, queues, procfs entries, sysfs, and debugfs; there is no persistent storage.

## Integration Points
Protocol modules such as BNEP, RFCOMM, HIDP, SCO, L2CAP, HCI, and ISO register through this file. It integrates with Linux sockets, procfs, debugfs, sysfs, LED triggers, ethtool timestamp queries via HCI, module autoloading, and BlueZ userspace-visible AF_BLUETOOTH sockets.

## Risks
The protocol dispatch table must be accessed under the rwlock; create callbacks are invoked while the read lock is held, so deadlocks are possible if protocol create paths re-enter registration. Accept dequeuing restarts after concurrent unlink to avoid unsafe list traversal, but socket lifetime depends on precise `sock_hold()`/`sock_put()` pairing. Stream receive mutates skb fragments manually; partial pulls must preserve skb length invariants. `bt_init()` does not initialize ISO but `bt_exit()` calls `iso_exit()`, which relies on the called function being safe for the selected build/config state.

## Test Signals
Signals include successful protocol module autoload, AF_BLUETOOTH socket creation per protocol, accept/defer setup behavior, recvmsg ancillary data, poll state transitions, ethtool timestamp ioctl on `hciX`, `/proc/net` protocol listings, debugfs root creation/removal, and fault-injection coverage for each init cleanup label.
