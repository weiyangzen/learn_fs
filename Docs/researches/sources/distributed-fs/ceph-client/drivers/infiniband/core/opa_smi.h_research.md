# sources/distributed-fs/ceph-client/drivers/infiniband/core/opa_smi.h

## Purpose
`opa_smi.h` declares Omni-Path Architecture SMI directed-route helpers and provides inline checks for whether an OPA SMP should be handled locally by a device's SMA/SM `process_mad` callback.

## Important APIs, types, and functions
- `opa_smi_handle_dr_smp_recv()` updates or validates an inbound OPA directed-route SMP according to switch/endport role, current port, and physical port count.
- `opa_smi_get_fwd_port()` returns the port to use when forwarding an OPA directed-route SMP.
- `opa_smi_check_forward_dr_smp()` classifies an OPA DR SMP as local, send, forward, or discard.
- `opa_smi_handle_dr_smp_send()` handles outgoing OPA DR SMP path updates and validation.
- `opa_smi_check_local_smp()` returns `IB_SMI_HANDLE` for outbound-direction DR SMPs that have reached the end of their directed route and can be passed to `device->ops.process_mad`.
- `opa_smi_check_local_returning_smp()` returns `IB_SMI_HANDLE` for returning DR SMPs whose hop pointer has reached zero and can be passed to the local SM.

## Control flow
The inline local checks are used by `mad.c` before deciding whether an OPA directed-route SMP should be sent on QP0, forwarded, discarded, or processed locally. They require a device `process_mad` callback and inspect OPA SMP direction, `hop_ptr`, and `hop_cnt`.

## State and persistence
The header owns no state. It reads fields from `struct opa_smp` and the RDMA device ops table. Any path mutation happens in the out-of-line helpers declared here.

## Dependencies and integration points
It depends on public IB and OPA SMI headers plus the local `smi.h` action enums. Its main consumer in this subset is `mad.c`, which uses it for OPA-specific DR SMP processing alongside classic IB SMI helpers.

## Risks
- The local-handle predicates encode OPA spec hop-pointer rules. Off-by-one changes can misroute management packets or prevent local SMA/SM handling.
- The checks require `device->ops.process_mad`; devices without that callback must discard local handling even if the path position matches.
- OPA and classic IB SMP structures are similar but not interchangeable; callers must only use these helpers on OPA SMPs.

## Test signals
- Directed-route OPA MAD tests should cover start, intermediate, local end, returning end, and discard cases.
- Build coverage should include OPA-capable RDMA configurations and classic IB-only configurations to catch include and type drift.
