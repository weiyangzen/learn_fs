# sources/distributed-fs/lustre-release/lnet/selftest/console.c

## Purpose
Implements the kernel-side LNet Selftest console object model: sessions, nodes, groups, batches, tests, debug/stat queries, join-session acceptor service, and console init/fini.

## Important APIs And Functions
Global state is `console_session`. Node/group helpers include `lstcon_node_find()`, `lstcon_node_put()`, `lstcon_group_find()`, `lstcon_group_addref()`, and `lstcon_group_decref()`. Public operations include `lstcon_session_new()`, `lstcon_session_end()`, group/node add/remove/clean/refresh APIs, batch add/run/stop/list/info APIs, `lstcon_test_add()`, stat/debug APIs, `lstcon_acceptor_handle()`, `lstcon_console_init()`, and `lstcon_console_fini()`.

## Control Flow
Session creation validates features, creates a session id, adds the default batch, starts the RPC pinger, and marks the console active. Group node add/remove flows use temporary groups and `conrpc.c` transactions to invite or remove remote nodes. Test add verifies idle batch and active source/destination groups, sends server-add RPCs first, then client-add RPCs with destination bulk. Batch run/stop/query dispatches batch transactions to client nodes. Session end posts remove-session RPCs, stops the pinger, waits for orphan RPC cleanup, and destroys batches, groups, and nodes.

## State And Persistence
All state is volatile in `console_session`: mutex-protected session identity, object lists, node hash, batches, groups, transaction list, RPC freelist, feature masks, and pinger. Reference counts protect nodes/groups during tests and concurrent operations.

## Dependencies And Integration Points
Uses `conrpc.c` for transactions, SRPC services from `rpc.c`/`framework.c`, netlink init/fini, LNet ioctl notifier registration, LNet NID conversion, and user-copy helpers.

## Risks
Manual refcounting is delicate. Partial remote test-add failures still leave local test descriptors for inspection. Join-session handling must avoid modifying busy groups. Shutdown lock ordering with pinger/RPC callbacks is critical.

## Test Signals
Cover force session recreation, duplicate group/batch rejection, busy group rejection, node add/remove/refresh, partial test-add failures, batch state transitions, join wrong-session/feature errors, and final empty-list/hash assertions.
