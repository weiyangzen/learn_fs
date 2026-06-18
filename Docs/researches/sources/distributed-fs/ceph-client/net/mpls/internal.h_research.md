<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/internal.h -->
# sources/distributed-fs/ceph-client/net/mpls/internal.h

## Purpose
Defines private MPLS data structures and helpers shared by MPLS core, GSO, and lightweight tunnel support. It centralizes route/nexthop layout, decoded label representation, per-device state, counter update macros, payload type constants, and netlink label helper prototypes.

## Important APIs, Types, and Functions
`struct mpls_entry_decoded` holds decoded label, TTL, traffic class, and BOS. `struct mpls_dev` stores per-netdevice MPLS enablement, stats, sysctl, and RCU freeing. `struct mpls_nh` and `struct mpls_route` define the contiguous LFIB route memory layout. `MPLS_NH_VIA_OFF()`, `MPLS_NH_SIZE()`, `for_nexthops()`, and `change_nexthops()` encode iteration and alignment rules. `mpls_entry_decode()`, `mpls_dev_rcu()`, and `mpls_dev_get()` are inline helpers. Prototypes expose `nla_put_labels()`, `nla_get_labels()`, `mpls_output_possible()`, `mpls_dev_mtu()`, `mpls_pkt_too_big()`, and `mpls_stats_inc_outucastpkts()`.

## Control Flow
This header has no runtime control flow beyond inline decode and RCU dereference helpers. Its macros shape the route allocation and iteration control flow used by `af_mpls.c`: every route contains a fixed-size sequence of nexthop records, each followed by an aligned via address area whose offset is computed from the route's maximum label and address sizes.

## State and Persistence
No global state is defined. The header specifies the persistent in-memory state owned elsewhere: `mpls_dev` attached to `net_device::mpls_ptr`, per-CPU link stats, and `mpls_route` objects stored in namespace LFIB arrays. The stat macros select different synchronization strategies for 32-bit versus 64-bit architectures.

## Dependencies and Integration Points
Depends on `<net/mpls.h>`, netdevice RCU pointers, netlink attributes, and kernel per-CPU stat synchronization. It is consumed by `af_mpls.c` and `mpls_iptunnel.c`, and its exported prototypes also serve MPLS tunnel code that needs label serialization and output feasibility checks.

## Risks
The route memory layout is ABI-like inside the module: offset and size macros must stay synchronized with allocation, nexthop iteration, and via access. `rt_nh_size` and `rt_via_offset` are `u8`, so allocation limits in `af_mpls.c` are part of the safety contract. Counter macros assume a valid allocated per-CPU stats pointer and correct BH/seqcount protection on 32-bit systems.

## Test Signals
Compile-time coverage from MPLS core and tunnel modules is the main header signal. Runtime signals include correct route dumps for multipath nexthops with labels/via addresses, no KASAN/alignment faults under route add/delete, and correct per-device stats on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/internal.h -->
