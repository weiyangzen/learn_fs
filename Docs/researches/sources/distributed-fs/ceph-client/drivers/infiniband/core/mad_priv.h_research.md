# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_priv.h

## Purpose
`mad_priv.h` defines the private data model shared by the MAD core and RMPP implementation. It captures queue limits, registration-table dimensions, per-agent and per-port state, send work request state, local completion records, and internal helper prototypes.

## Important APIs, types, and functions
- Queue constants define default, minimum, and maximum MAD send/receive depths plus SGE counts for MAD WRs.
- Registration constants define maximum management class, class version, vendor OUI slots, and vendor range-2 table size.
- `struct ib_mad_private_header` and `struct ib_mad_private` wrap receive buffers with the CQE/list linkage, receive WC, raw WC, DMA mapping, GRH, variable MAD data, and the port's maximum MAD size.
- `struct ib_mad_agent_private` adds private queues, counters, RMPP receive list, timeout and local work items, registration request, and lifetime management around a public `struct ib_mad_agent`.
- `enum ib_mad_state` documents the legal lifecycle of a send work request from construction through backlog, send, wait, early response, cancellation, and completion.
- `struct ib_mad_send_wr_private` combines the public send buffer with UD send WR, two SGEs, DMA mappings, retry state, RMPP segment state, and solicited-flow-control flag.
- `expect_mad_state*()` and `not_expect_mad_state()` provide lockdep-enabled assertions for state-machine transitions.
- Internal prototypes expose `ib_send_mad()`, `ib_find_send_mad()`, `ib_mad_complete_send_wr()`, `ib_mark_mad_done()`, `ib_reset_mad_timeout()`, and `change_mad_state()` to `mad_rmpp.c`.

## Control flow
The header does not execute code directly, but it defines the structures that make `mad.c` and `mad_rmpp.c` interoperate. `mad.c` owns port creation, agent registration, state transitions, and completion dispatch. `mad_rmpp.c` uses the shared send WR fields to advance segment windows and uses the shared receive list on `ib_mad_agent_private` to track inbound multi-packet transfers.

## State and persistence
All state described here is volatile kernel state. Queue counters mirror list membership and active QP WRs. Agent reference counting is paired with a completion for synchronous teardown and an RCU head for final free. Per-port registration tables persist while a MAD-capable port is open and are expected to be empty once agents unregister.

## Dependencies and integration points
The header depends on RDMA public MAD/SMI headers, workqueues, completions, and InfiniBand WC/QP types. Its definitions are consumed by `mad.c`, `mad_rmpp.c`, and related core helpers that need private access to send matching, timeout, RMPP, and registration internals.

## Risks
- Structure layout changes can break assumptions in container-of conversions from CQEs, receive WCs, send buffers, and list entries.
- Queue counters and list membership must stay synchronized; many call sites rely on `count` as a resource limit rather than recomputing list length.
- `__packed` on receive buffer wrappers makes alignment a consideration if fields are added.
- State assertion helpers only warn under lockdep, so invalid transitions still need runtime tests.

## Test signals
- Compile all MAD/RMPP users after any structure or prototype change.
- Use lockdep-enabled tests to exercise normal sends, timeouts, cancellation, early responses, and RMPP segmentation so state assertions can fire.
- Run KASAN/KCSAN style testing around agent unregister and receive free paths because the header encodes most lifetime relationships.
