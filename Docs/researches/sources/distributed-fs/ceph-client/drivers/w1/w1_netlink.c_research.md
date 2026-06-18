# sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c` implements the kernel side of the 1-Wire connector/netlink API when `CONFIG_W1_CON` and connector support are available. It accepts userspace connector messages, dispatches master and slave commands to the 1-Wire core, formats replies and command status records, sends asynchronous notifications for master/slave events, and provides empty stubs when the connector path is not built. The complete 740-line source was read for this report.

## Important APIs, Types, and Functions

The public entry points are `w1_netlink_send()`, `w1_init_netlink()`, and `w1_fini_netlink()`. `w1_init_netlink()` registers `w1_cn_callback()` with connector id `CN_W1_IDX/CN_W1_VAL`; `w1_fini_netlink()` unregisters it. Internal state is centered on `struct w1_cb_block`, a single allocation containing a copied request, async nodes, and a reply buffer, and `struct w1_cb_node`, which embeds `struct w1_async_cmd` for the master worker thread. Important helpers include `w1_reply_len()`, `w1_reply_make_space()`, `w1_netlink_setup_msg()`, `w1_netlink_queue_cmd()`, `w1_netlink_queue_status()`, `w1_netlink_send_error()`, `w1_process_command_master()`, `w1_process_command_slave()`, `w1_process_cb()`, `w1_list_count_cmds()`, and `w1_process_command_root()`.

## Control Flow

Kernel notifications use `w1_netlink_send()` to wrap a `struct w1_netlink_msg` inside a connector message and broadcast it. Userspace requests enter `w1_cn_callback()`, which validates connector flags, scans all embedded `w1_netlink_msg` records to count async work nodes and estimate reply space, allocates a `w1_cb_block`, and then walks the message stream again. `W1_LIST_MASTERS` is handled synchronously by `w1_process_command_root()`. `W1_MASTER_CMD` and `W1_SLAVE_CMD` resolve a master or slave, take the relevant references, enqueue a `w1_async_cmd` on the master's `async_list`, and wake the master thread. The worker invokes `w1_process_cb()`, locks `bus_mutex`, optionally resets/selects the slave, iterates embedded `w1_netlink_cmd` records, executes I/O, reset, search, list, add, or remove operations, and queues both data replies and status replies. When the block reference count drops to zero, `w1_unref_block()` sends any pending bundled reply and frees the allocation.

## State and Persistence Behavior

All persistent kernel state belongs to the 1-Wire core: master lists, slave lists, slave references, master reference counts, and the master's async queue. This file owns only transient request/reply state in `w1_cb_block`. `block->request_cn` preserves the original connector message while `block->first_cn`, `block->cn`, `block->msg`, and `block->cmd` advance through an in-place reply buffer. `block->refcnt` protects the reply buffer across async nodes; the initial callback and each queued node hold references. No state is written to disk. Replies may be bundled when `W1_CN_BUNDLE` is set, or flushed early after each command when bundling is not requested.

## Dependencies and Integration Points

The file depends on connector/netlink (`cn_add_callback`, `cn_del_callback`, `cn_netlink_send`, `cn_netlink_send_mult`), skbuff netlink metadata for `portid`, the 1-Wire core structures and helpers from `w1_internal.h`, and message definitions from `w1_netlink.h`. Integration points include `w1_masters`, `w1_mlock`, `w1_search_master_id()`, `w1_search_slave()`, `w1_unref_slave()`, `w1_slave_found()`, `w1_search_process_cb()`, `w1_reset_bus()`, `w1_reset_select_slave()`, block read/write/touch helpers, and slave attach/detach helpers.

## Risks and Edge Cases

The code parses variable-length nested messages and relies on careful length checks before advancing pointers; malformed `len` fields are rejected with `-E2BIG` or `-EPROTO`. `w1_netlink_msg.status` is an 8-bit field populated with `(u8)-error`, so consumers must interpret status as the protocol expects. Reply construction is in-place and split by `CONNECTOR_MAX_MSG_SIZE`; incorrect size estimates could fragment replies or force early sends. `dev->priv` is temporarily used as a back pointer during processing under `bus_mutex`, so any future users of that field would conflict. The async enqueue path can send direct errors after other async work is live because the shared reply block is not locked in the callback. Stub builds silently discard notifications and report successful init.

## Test Signals

Useful checks include compiling with connector enabled and disabled; userspace tests for `W1_LIST_MASTERS`, master commands, slave commands, search/list-slave replies, add/remove error cases, and unknown flags; malformed nested length fuzzing; bundled and unbundled reply-size boundary tests; and concurrency tests where multiple master/slave command messages share one connector request while slaves appear or disappear.
