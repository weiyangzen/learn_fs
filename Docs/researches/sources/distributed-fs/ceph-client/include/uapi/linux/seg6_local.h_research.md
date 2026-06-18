<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h

Purpose: defines SRv6 local SID action IDs, behavior attributes, counters, flavors, and nested flavor operations used by rtnetlink route configuration.

Important APIs, types, and functions: action enum values cover End, End.X, End.T, End.DX2, End.DX6, End.DX4, End.DT6, End.DT4, End.B6, End.B6.Encaps, End.BM, End.S, End.AS, End.AM, lookup-table variants, and NEXT_CSID behavior. Attribute IDs include action, SRH, table, nexthop, interface, counters, flavors, and VRF table. Counter structs expose packet/byte/error counters. Flavor enums include PSP, USP, USD, and NEXT_CSID with next-csid length attributes.

Control flow: userspace configures a local SID route with action and action-specific attributes. Kernel route code validates mandatory attributes, installs seg6local state, and executes the behavior when a packet reaches the local SID.

State and persistence behavior: local SID behavior state persists in route entries and may maintain counters. The header only defines serialized configuration and dump layouts.

Dependencies and integration points: integrates with SRv6 local processing, rtnetlink route attributes, VRFs, nexthop/interface lookup, counters, and iproute2 `seg6local`.

Risks and edge cases: each action requires a different attribute set; accepting missing or extra attributes can misroute traffic. Counter sizes, flavor nesting, NEXT_CSID bit lengths, and table/VRF handling are common validation risks.

Test signals: install and dump every local action, exercise PSP/USP/USD/NEXT_CSID flavors, verify counters increment, reject invalid attribute combinations, and route packets through End.DX/DT/B6 behaviors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_local.h -->
