# sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.h

## Purpose
`smi.h` declares the SMI directed-route decision APIs and provides inline checks for when a directed-route SMP should be handled by the local SMA/SM.

## Important APIs, types, and functions
- `enum smi_action` has `IB_SMI_DISCARD` and `IB_SMI_HANDLE`.
- `enum smi_forward_action` has `IB_SMI_LOCAL`, `IB_SMI_SEND`, and `IB_SMI_FORWARD`.
- Declared functions: `smi_handle_dr_smp_recv()`, `smi_handle_dr_smp_send()`, `smi_check_forward_dr_smp()`, and `smi_get_fwd_port()`.
- Inline helpers: `smi_check_local_smp()` and `smi_check_local_returning_smp()`.

## Control flow and behavior
The inline local checks require a device `process_mad` callback. For outbound directed-route SMPs, local handling is allowed when direction is outbound and `hop_ptr == hop_cnt + 1`. For returning SMPs, local handling is allowed when direction is returning and `hop_ptr == 0`. Otherwise packets are discarded by the local check, leaving forwarding code to make the broader routing decision.

## State, persistence, and dependencies
The header has no persistent state. It depends on `struct ib_smp`, `struct ib_device`, and `ib_get_smp_direction()` from RDMA SMI headers.

## Integration points
Included by `smi.c` and MAD/SMA handling paths that need a compact local-vs-forward decision before calling device `process_mad`.

## Risks and test signals
Risks are subtle spec condition regressions and changes to `process_mad` availability semantics. Test signals include local process_mad decisions for outbound and returning paths, no-process_mad devices, and comparison with full `smi.c` forwarding decisions.
