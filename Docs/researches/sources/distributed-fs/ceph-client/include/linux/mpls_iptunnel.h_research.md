<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h

## Purpose
`mpls_iptunnel.h` exposes kernel code to the UAPI definitions for MPLS IP tunnel attributes.

## Important APIs, Types, and Functions
It only includes `uapi/linux/mpls_iptunnel.h`.

## Control Flow and State
No local control flow exists. Tunnel code uses the imported UAPI constants and structures.

## State and Persistence Behavior
No state is declared here. Tunnel configuration is managed by networking subsystems and netlink.

## Dependencies and Integration Points
It integrates MPLS tunnel implementation code with userspace netlink ABI definitions.

## Risks
The main risk is assuming additional local helpers exist; this file is a thin ABI include. UAPI changes drive behavior.

## Test Signals
MPLS tunnel netlink configuration tests and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mpls_iptunnel.h -->
