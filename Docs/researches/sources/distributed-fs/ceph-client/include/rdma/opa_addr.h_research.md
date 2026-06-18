# sources/distributed-fs/ceph-client/include/rdma/opa_addr.h

Purpose: Omni-Path address helpers for detecting special OPA GIDs, extracting extended LIDs, and validating unicast LID ranges for IB versus OPA address handles.

Important APIs/types/functions: `OPA_SPECIAL_OUI`, `OPA_MAKE_ID`, `OPA_TO_IB_UCAST_LID`, `OPA_GID_INDEX`, `OPA_MCAST_NR`, `OPA_COLLECTIVE_NR`, `ib_is_opa_gid`, `opa_get_lid_from_gid`, `opa_is_extended_lid`, `opa_get_mcast_base`, and `rdma_is_valid_unicast_lid`.

Control flow: Helpers inspect GID/LID values and branch on address-handle type. IB unicast validation rejects zero and LIDs at or above the IB multicast base; OPA validation rejects zero and LIDs at or above the OPA multicast base.

State and persistence behavior: Stateless inline conversions/validators over caller-provided IDs.

Dependencies and integration points: Depends on `opa_smi.h`, `ib_verbs.h` AH accessors, endian helpers, and IB LID constants. Integrates with OPA AH/path validation and management paths.

Risks: Host/big-endian mixups can invalidate legitimate paths. Extended LIDs cannot be blindly truncated for IB consumers. Multicast base assumptions must match fabric LID width.

Test signals: OPA GID detection, LID extraction, extended-LID boundaries, multicast/collective ranges, and valid/invalid IB and OPA DLIDs.
