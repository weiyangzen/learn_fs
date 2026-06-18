# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/opa_compat.h

## Purpose
`opa_compat.h` provides local OPA definitions and helpers that HFI1 needs before or beyond generic Linux RDMA core coverage. In this subset it mainly supplies OPA management attribute IDs, PMA status codes, port-state helpers, and OPA physical port-state enumeration.

## Important APIs, types, and functions
- OPA SMA attribute IDs define congestion info, HFI congestion log, HFI congestion setting, and congestion control table.
- OPA PMA attribute IDs define port status, clear port status, data counters, error counters, and error info.
- `OPA_PM_STATUS_REQUEST_TOO_LARGE` is a PMA response status used when computed replies exceed MAD payload size.
- `port_states_to_logical_state()` and `port_states_to_phys_state()` decode fields from `struct opa_port_states`.
- `enum opa_port_phys_state` extends familiar IB physical states with OPA offline and test states and documents valid read/write ranges.

## Control flow
There is no standalone control flow. `mad.c` includes this header through `mad.h` and uses its constants and inline decoders during SMA/PMA dispatch and PortInfo/PortStateInfo handling.

## State and persistence
The header defines constants and inline helpers only. It owns no state.

## Dependencies and integration points
The helpers assume RDMA OPA structures such as `struct opa_port_states` are available from included RDMA headers. The definitions are part of HFI1's management protocol compatibility surface.

## Risks
- Values must match OPA management specifications and any upstream RDMA core definitions. Divergence would break fabric-manager interoperability.
- The physical state enum documents that only values 0..3 are valid on writes while more values are returned on reads; SET handlers must preserve that distinction.
- The include guard name `_LINUX_H` is broad and could conflict with other headers if included in unusual orders.

## Test signals
- Compile all HFI1 MAD users after RDMA core OPA header updates.
- Exercise PortStateInfo and PortInfo GET/SET paths that use logical and physical state decoders.
- Check for macro value duplication if generic RDMA headers gain equivalent definitions.
