# sources/distributed-fs/ceph-client/net/tipc/trace.h

## Purpose
Declares the TIPC tracepoint system, dump-size constants, symbolic event/state printers, helper prototypes, and trace event classes for skbs, skb lists, sockets, links, nodes, finite-state machines, and bearer device events.

## Important APIs, Types, And Macros
The header defines dump masks such as `TIPC_DUMP_TRANSMQ`, `TIPC_DUMP_SK_RCVQ`, and `TIPC_DUMP_ALL`; symbolic macros `state_sym`, `evt_sym`, and `dev_evt_sym`; helper prototypes for skb/list/socket/link/node dumps and socket filtering; event classes `tipc_skb_class`, `tipc_list_class`, `tipc_sk_class`, `tipc_link_class`, `tipc_link_transmq_class`, `tipc_node_class`, and `tipc_fsm_class`; and concrete events such as `tipc_sk_sendmsg`, `tipc_sk_filter_rcv`, `tipc_link_retrans`, `tipc_node_timeout`, and `tipc_l2_device_event`.

## Control Flow And State
The tracepoint declarations generate static tracepoints when included normally and definitions when included by `trace.c`. Conditional socket events call `tipc_sk_filtering`, while overload events add a second condition. Dynamic arrays are sized based on whether deep queue dumps are requested.

## Dependencies And Integration Points
Includes Linux tracepoint infrastructure and TIPC core, link, socket, and node headers. Trace calls are scattered through socket, link, node, bearer, and protocol receive paths, and `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` are set so kernel trace generation can find this header.

## Risks And Test Signals
Risks include tracepoint ABI churn, helper functions being unavailable under include-order changes, and expensive deep dumps on hot paths. Test signals include compiling with tracepoints enabled, enabling each event class through tracing, confirming socket filter conditions work, and checking that link/node FSM symbolic output matches actual state transitions.
