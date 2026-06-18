<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls.h -->
# sources/distributed-fs/ceph-client/include/linux/mpls.h

## Purpose
`mpls.h` provides kernel-side convenience masks for decoded MPLS label stack fields.

## Important APIs, Types, and Functions
It includes UAPI MPLS definitions and derives `MPLS_TTL_MASK`, `MPLS_BOS_MASK`, `MPLS_TC_MASK`, and `MPLS_LABEL_MASK` by shifting the UAPI label-stack masks.

## Control Flow and State
No functions are implemented. Callers use the masks while parsing or constructing MPLS label stack entries.

## State and Persistence Behavior
No state is owned. MPLS packet metadata is transient network data.

## Dependencies and Integration Points
It depends on `uapi/linux/mpls.h` and integrates with MPLS routing, tunnel, and packet parsing code.

## Risks
Masks must stay aligned with UAPI shift definitions. Incorrect masks corrupt TTL, bottom-of-stack, traffic class, or label extraction.

## Test Signals
MPLS packet parse/build tests and compile checks against UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls.h -->
