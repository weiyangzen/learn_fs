# sources/distributed-fs/ceph-client/net/phonet/pep.c

## Purpose
`pep.c` implements the Phonet Pipe End Point protocol (`PN_PROTO_PIPE`) for PF_PHONET `SOCK_SEQPACKET` sockets. It provides pipe connection setup, accept/connect semantics, flow-control negotiation, control request handling, data transfer, pipe removal/disconnect, socket options, and optional GPRS netdev encapsulation support.

## Important APIs, types, and functions
Protocol registration is `pep_register()`/`pep_unregister()` around `pep_pn_proto` and `pep_proto`. Socket callbacks include `pep_sock_close()`, `pep_sock_accept()`, `pep_sock_connect()`, `pep_ioctl()`, `pep_init()`, `pep_setsockopt()`, `pep_getsockopt()`, `pep_sendmsg()`, `pep_recvmsg()`, `pep_do_rcv()`, `pep_sock_unhash()`, and common Phonet hash/port helpers.

Packet formatting helpers are `pep_alloc_skb()`, `pep_reply()`, `pep_indicate()`, `pipe_handler_request()`, `pipe_handler_send_created_ind()`, `pep_accept_conn()`, `pep_reject_conn()`, and `pep_ctrlreq_error()`. Flow-control helpers include `pipe_negotiate_fc()`, `pipe_rcv_created()`, `pipe_rcv_status()`, `pipe_grant_credits()`, `pipe_start_flow_control()`, `pep_writeable()`, `pipe_skb_send()`, `pep_write()`, and `pep_read()`.

Receive dispatch is split between listening/unconnected routing in `pep_do_rcv()`, connected accepted sockets in `pipe_do_rcv()`, and active connector handling in `pipe_handler_do_rcv()`.

## Control flow and state
PEP maps protocol state to TCP-style socket states: `TCP_CLOSE` unused, `TCP_LISTEN` listener, `TCP_SYN_SENT` connection or enable pending, `TCP_SYN_RECV` connected but disabled, `TCP_ESTABLISHED` enabled, and `TCP_CLOSE_WAIT` disconnected. `struct pep_sock` stores listener link, child pipe hlist, control request queue, pipe handle, peer type, flow-control mode, TX credits, RX credits, initial enable state, alignment mode, and optional GPRS ifindex.

Server-side flow starts with a listening socket receiving `PNS_PEP_CONNECT_REQ` in `pep_do_rcv()`, queuing it on the listener accept queue. `pep_sock_accept()` dequeues the request, parses sub-blocks, validates requested state and duplicate pipe handle, allocates a child sock, initializes connected pipe state, sends a connect response with supported flow controls, and links the child under the listener hlist.

Client-side connect sends `PNS_PEP_CONNECT_REQ` through `pipe_handler_request()` and sets `TCP_SYN_SENT`; `pipe_handler_do_rcv()` processes `PNS_PEP_CONNECT_RESP`, negotiates flow controls, sends created indication, and transitions to `TCP_SYN_RECV` or `TCP_ESTABLISHED` depending on `init_enable`. Enable requests similarly wait for enable response and indication.

Data receive handles `PNS_PIPE_DATA` and `PNS_PIPE_ALIGNED_DATA` by stripping pipe headers, applying RX credits when flow-safe, queueing skbs, and waking readers. Data send requires `MSG_EOR`, waits for established state and positive TX credits, prepends the correct pipe data header, decrements credits atomically, and restores credits on send failure. Control requests are queued separately on `ctrlreq_queue` and exposed through OOB/urgent receive behavior.

Close sends disconnect/remove requests for active pipes, sets `TCP_CLOSE`, detaches any GPRS netdev, and drops the extra self reference taken around `sk_common_release()`.

## State and persistence behavior
All state is per socket and memory resident. Listener sockets own child pipe hlist membership. Accepted child sockets hold a reference on the listener until unhash. Flow-control credits are runtime counters; stats are mainly socket drops and queue lengths. `PNPIPE_ENCAP` can create a netdev whose lifetime is tied to the socket option and socket close.

## Dependencies and integration points
`pep.c` depends on PF_PHONET common socket plumbing, `pn_skb_send()`, Phonet sockaddr helpers, generic socket queue/wait APIs, TCP state constants, and the GPRS adapter in `pep-gprs.c`. It registers as a separate `pn_pep` module and can be autoloaded by PF_PHONET protocol requests.

## Risks and edge cases
Risks include state-machine mismatches, credit underflow/overgrant, child/listener lifetime errors, control queue growth, skb ownership after reply/error paths, and blocking connect/send wait behavior under signals or close. The `pep_setsockopt()` expression `if (!pn->ifindex == !val)` is logically intentional but easy to misread; changes there can break attach/detach idempotence. GPRS attachment requires careful lock release and reacquisition because it calls netdev registration code.

## Test signals
Test listener accept, duplicate pipe handles, invalid connect sub-blocks, active connect/enable success and failure, disconnect/reset/disable indications, one-credit and multi-credit flow control, TX blocking and `MSG_DONTWAIT`, OOB control requests, `SIOCINQ`, `SIOCPNENABLEPIPE`, `PNPIPE_HANDLE`, `PNPIPE_INITSTATE`, `PNPIPE_ENCAP`, listener unhash with children, and module autoload/unload.
