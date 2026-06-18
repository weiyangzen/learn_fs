# sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.c

## Purpose
`smi.c` implements Directed Route Subnet Management Packet handling for InfiniBand and OPA. It updates hop pointers and return paths, decides whether a packet should be handled, discarded, sent locally, or forwarded, and extracts the next forwarding port.

## Important APIs, types, and functions
- IB APIs: `smi_handle_dr_smp_send()`, `smi_handle_dr_smp_recv()`, `smi_check_forward_dr_smp()`, and `smi_get_fwd_port()`.
- OPA equivalents: `opa_smi_handle_dr_smp_send()`, `opa_smi_handle_dr_smp_recv()`, `opa_smi_check_forward_dr_smp()`, and `opa_smi_get_fwd_port()`.
- Shared static engines: `__smi_handle_dr_smp_send()`, `__smi_handle_dr_smp_recv()`, and `__smi_check_forward_dr_smp()`.

## Control flow and behavior
The send and receive helpers implement the IB spec C14 directed-route rules. They first reject unreasonable hop counts, then branch on direction. Outbound SMPs increment hop pointers as they move along `initial_path`, require switch capability for intermediate forwarding, and allow local handling at the end of a directed route based on switch status or permissive DLID. Returning SMPs decrement hop pointers along `return_path`, enforce switch-only intermediate forwarding, and allow local handling at the return endpoint based on permissive SLID. Receive handling also records `return_path[hop_ptr] = port_num` for outbound packets so responses can retrace the route.

## State, persistence, and dependencies
The file has no global state. It mutates fields inside caller-provided `ib_smp` or `opa_smp`: `hop_ptr`, `return_path`, and route interpretation. It depends on `<rdma/ib_smi.h>`, `opa_smi.h`, and direction/permissive-LID helpers.

## Integration points
Used by MAD/SMA paths that process or forward directed-route SMPs for switches, HCAs, and OPA devices. `smi.h` provides local handling checks used around these functions.

## Risks and test signals
Risks are off-by-one access to `initial_path[hop_ptr + 1]` and `return_path[hop_ptr - 1]`, wrong permissive LID handling, divergence between IB and OPA wrappers, and switch/HCA forwarding mistakes. Test signals include directed-route send/receive vectors for every C14 branch, invalid hop counts, zero-hop routes, permissive and non-permissive endpoints, switch versus non-switch behavior, and OPA route field parity.
