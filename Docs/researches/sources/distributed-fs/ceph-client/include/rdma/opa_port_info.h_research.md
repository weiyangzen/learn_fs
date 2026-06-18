# sources/distributed-fs/ceph-client/include/rdma/opa_port_info.h

Purpose: OPA PortInfo constants, masks, enums, and packed wire layout for subnet management queries and configuration of OPA port state.

Important APIs/types/functions: Link mode, packet format, LTP CRC mode, link-down reason, link-init reason, speed/width, and capability constants; `enum port_info_field_masks`; `struct opa_port_states`; `struct opa_port_state_info`; packed `struct opa_port_info` with LID, VL, port state, P_Key/Q_Key counters, link modes, packet formats, flit/preemption, error action, pass-through, M_Key, subnet prefix, neighbor MTU/queue state, IP addresses, neighbor GUID, capability masks, diagnostics, replay depth, neighbor mode, MTU cap, response time, and local port.

Control flow: Declarative wire layout. Consumers parse an OPA SMP PortInfo payload, use masks/endian conversions to extract packed fields, and write updated values for port modify operations.

State and persistence behavior: Mirrors management-plane port state in transient MAD/SMP buffers. Durable configuration resides in hardware/fabric manager state.

Dependencies and integration points: Depends on `opa_smi.h`. Integrates with OPA subnet management, port query/modify, and generic RDMA port attribute reporting.

Risks: Packed struct layout and masks must match the OPA spec. Endian conversion is caller responsibility. Reserved/removed fields must not be treated as valid capabilities.

Test signals: Struct size/layout checks, mask extraction for packed fields, endian round trips, PortInfo query/modify, link-state reason decoding, and reserved bit handling.
