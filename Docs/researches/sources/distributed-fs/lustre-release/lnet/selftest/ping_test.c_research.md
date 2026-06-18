# sources/distributed-fs/lustre-release/lnet/selftest/ping_test.c

## Purpose
Implements the ping test client and server for LNet Selftest. It sends simple no-bulk ping RPCs with magic, sequence, and timestamp fields, validates replies, and records ping errors.

## Important APIs And Functions
Defines `LST_PING_TEST_MAGIC`, module parameter `ping_srv_workitems`, `lst_ping_data`, client ops (`ping_client_init()`, `ping_client_fini()`, `ping_client_prep_rpc()`, `ping_client_done_rpc()`), server handler `ping_server_handle()`, and registration helpers `ping_init_test_client()` and `ping_init_test_service()`.

## Control Flow
Client init resets the sequence counter. Each prepared RPC is created by `sfw_create_test_rpc()`, filled with magic, sequence, and real-time timestamp, and posted by the framework. Completion checks transport status, byte-swaps replies if needed, validates magic and sequence, increments session ping errors on failure, and logs latency on success. The server validates request magic/type, echoes sequence/magic, and handles unsupported feature masks with `EPROTO`.

## State And Persistence
The global sequence counter is volatile and reset per client test instance. Error counts are stored in `sfw_session.sn_ping_errors`. No data persists after session teardown.

## Dependencies And Integration Points
Plugs into framework test registration via `sfw_test_client_ops` and `srpc_service`. Uses SRPC ping wire structs and framework RPC creation/completion.

## Risks
The sequence counter is module-global, so concurrent ping client instances share it. Latency uses real time and can be affected by clock changes. Feature mismatch is a reply-level status, not a transport failure.

## Test Signals
Valid round trips, bad magic, sequence mismatch, endian-swapped messages, transport failure error counts, and unsupported feature masks.
