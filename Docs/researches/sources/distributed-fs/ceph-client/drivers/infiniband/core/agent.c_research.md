# sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.c

## Purpose

`agent.c` implements the lightweight MAD agent support used by the InfiniBand core to send management responses on SMI and GSI QPs. It maintains a global list of per-device/per-port agent registrations and exposes helpers to open/close those registrations and to transmit response MADs back to the requester.

## Important APIs, Types, And Functions

- `struct ib_agent_port_private` stores list linkage and two optional MAD agents: `agent[0]` for `IB_QPT_SMI` and `agent[1]` for `IB_QPT_GSI`.
- `ib_agent_port_open()` allocates the private object and conditionally registers send-only MAD agents based on `rdma_cap_ib_smi()` and `rdma_cap_ib_cm()`.
- `ib_agent_port_close()` removes a port from the global list, unregisters any registered agents, and frees the private object.
- `agent_send_response()` locates the right registered agent, creates an AH from the receive WC/GRH, creates a send MAD, copies the supplied response header/body, and posts it.
- `agent_send_handler()` is the send-completion callback; it destroys the AH and frees the send MAD.

## Control Flow

Open flow: allocate `port_priv`, register SMI agent if supported, register GSI agent if supported, then append the object to `ib_agent_port_list` under `ib_agent_port_list_lock`. Error paths unwind GSI then SMI registration before freeing the object.

Send flow: `agent_send_response()` resolves the port entry by device and either real port or port 0 for switch devices. It selects the agent by `qpn`, creates an AH from the incoming WC, adjusts OPA response length for non-OPA base versions, creates a send MAD with the incoming source QP and P_Key index, copies the response payload, records the AH, fixes the internal send WR port for switch devices, and posts through `ib_post_send_mad()`. Failed post or allocation frees the send buffer and AH.

Close flow: remove the port entry from the global list while holding the spinlock, then unregister agents outside the lock and free memory.

## State And Persistence

All state is in kernel memory. The global list `ib_agent_port_list` is protected by `ib_agent_port_list_lock`. Each send allocates a transient `ib_mad_send_buf` and AH; ownership transfers to the MAD layer on successful post and returns via `agent_send_handler()`. There is no on-disk persistence or user-visible configuration.

## Dependencies And Integration Points

This file depends on the RDMA MAD layer (`ib_register_mad_agent()`, `ib_create_send_mad()`, `ib_post_send_mad()`), AH helpers (`ib_create_ah_from_wc()`, `rdma_destroy_ah()`), and capability helpers (`rdma_cap_ib_switch()`, `rdma_cap_ib_smi()`, `rdma_cap_ib_cm()`). It is integrated with SMI/GSI management paths that need to synthesize replies, including OPA-aware response sizing.

## Risks

- `qpn` is used as an index into a two-element array; callers must pass only 0 or 1.
- The lookup returns a port object after dropping the global spinlock. Correctness depends on lifecycle ordering that prevents concurrent close from freeing an entry while a sender still uses it.
- Switch devices use port 0 for registration lookup but later override the send WR port; regressions here can route responses out the wrong port.
- OPA response length normalization must preserve legacy MAD length expectations for non-OPA management base versions.

## Test Signals

Useful signals include MAD response success for SMI and GSI, correct AH teardown on send completion and post failure, error logs for missing port agents or AH/send allocation failures, and switch-device tests that validate response port override. Kernel tests or fault injection should cover partial registration failure and close-after-open cleanup.
