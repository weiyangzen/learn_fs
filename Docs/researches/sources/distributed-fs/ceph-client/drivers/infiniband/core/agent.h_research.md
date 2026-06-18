# sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.h

## Purpose

`agent.h` is the small internal interface for the InfiniBand core MAD response agent implemented in `agent.c`. It declares lifecycle entry points for per-port agent registration and the response send helper.

## Important APIs, Types, And Functions

- `ib_agent_port_open(struct ib_device *device, int port_num)` registers per-port send-only MAD agents where supported.
- `ib_agent_port_close(struct ib_device *device, int port_num)` tears down the previously opened agents.
- `agent_send_response(...)` sends a prepared MAD response using receive-side routing information, device/port identity, QP selector, response length, and OPA mode.

## Control Flow

The header has no executable control flow. It defines an include guard, imports `<linux/err.h>` and `<rdma/ib_mad.h>`, and exposes function prototypes consumed by other InfiniBand core modules.

## State And Persistence

No state is defined here. State is owned by `agent.c` and the RDMA MAD subsystem.

## Dependencies And Integration Points

The prototypes bind this module to `struct ib_device`, `struct ib_mad_hdr`, `struct ib_grh`, and `struct ib_wc`. Callers must already understand MAD header formats, receive completions, and whether the response is OPA-specific.

## Risks

- The `qpn` parameter in `agent_send_response()` is not type-safe; the implementation expects an SMI/GSI array index.
- The header exposes raw pointers and lengths, so callers must ensure `resp_mad_len` matches the payload actually available at `mad_hdr`.

## Test Signals

Build coverage is the primary signal for this header. Runtime coverage comes from callers successfully opening/closing agent ports and sending responses through both SMI and GSI paths.
