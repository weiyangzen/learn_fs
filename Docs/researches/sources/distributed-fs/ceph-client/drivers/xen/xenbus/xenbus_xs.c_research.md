<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c

## Purpose
`xenbus_xs.c` is the kernel-side Xenstore client library used by Xen bus code and the xenbus userspace device. It wraps Xenstore requests, replies, transactions, directory/read/write/remove helpers, and watch registration over `xenbus_comms`.

## Important APIs, types, and functions
Exports include `xenbus_directory`, `xenbus_exists`, `xenbus_read`, `xenbus_write`, `xenbus_rm`, `xenbus_transaction_start`, `xenbus_transaction_end`, `xenbus_scanf`, `xenbus_read_unsigned`, `xenbus_printf`, `xenbus_gather`, `register_xenbus_watch`, `unregister_xenbus_watch`, and `xenbus_dev_request_and_reply`. Internal request handling centers on `struct xb_req_data`, `xs_talkv`, `xs_single`, `xs_send`, `xs_wait_for_reply`, `read_reply`, `xs_request_enter`, and `xs_request_exit`.

## Control flow
Callers build a Xenstore message, queue an `xb_req_data` on `xb_write_list`, wake `xb_waitq`, then block until the response thread marks the request replied or aborted. Public helpers convert higher-level operations into `XS_*` commands. Watch messages arrive through `xs_watch_msg`, are matched by pointer token, queued on `watch_events`, and executed by the `xenwatch` kthread under `xenwatch_mutex`.

## State and persistence
State is runtime-only: suspend-critical counters, monotonic request IDs, registered watch list, pending watch events, per-request wait queues, and outstanding transaction accounting. `xs_state_users` intentionally counts normal requests and non-user transactions so suspend/resume waits until there are no open kernel Xenstore transactions.

## Dependencies and integration points
The file depends on Xenstore wire types, `xenbus_comms`, Xen domain state, reboot notifiers, kthreads, wait queues, rwsems, and spinlocks. It integrates with xenbus device probing, user-facing xenbus file operations, suspend/resume callbacks, and Xenstore watch notifications.

## Risks and test signals
Risks include request lifetime races, shutdown waits when Xenstore is unreachable, token reuse for watches, pending callbacks during unregister, and transaction accounting imbalance around failed start/end. Test signals include concurrent watches, unregister while callback is pending, suspend/resume with active transactions, reboot while waiting for replies, malformed watch bodies, and Xenstore error mapping coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c -->
