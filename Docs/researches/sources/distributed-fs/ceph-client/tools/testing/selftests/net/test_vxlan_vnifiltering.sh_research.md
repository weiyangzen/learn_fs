# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_vnifiltering.sh

## Purpose
`test_vxlan_vnifiltering.sh` validates the VXLAN VNI filtering API and datapath. It models hypervisors with multiple VM namespaces and overlapping VLANs, then verifies that external `vnifilter` VXLAN devices terminate only configured VNIs and interoperate with per-VNI remote/group configuration, multicast groups, traditional VXLAN devices, and metadata devices.

## Important APIs, Functions, and Types
The script sources `lib.sh` and defines `log_test`, `run_cmd`, `check_hv_connectivity`, `check_vm_connectivity`, `cleanup`, `setup-hv-networking`, `setup-vm`, and VNI-filter API cleanup/setup helpers. `setup-vm` is the central parameterized builder: it parses comma-separated VLAN/VNI attributes, creates VM VLAN interfaces and addresses, creates either traditional VXLAN devices or shared external `vnifilter`/metadata devices, enables bridge `vlan_tunnel`, adds tunnel mappings, and programs `bridge vni add` or FDB entries.

## Control Flow
Main checks root, `ip`, `ip link help vxlan` support for `vnifilter`, and `bridge vni` support. The API test creates a separate namespace and checks invalid and valid VNI-filter operations: `vnifilter` without `external`, duplicate VNI assignment across devices, VNI updates, per-VNI multicast group assignment, and immutable `vnifilter` flag changes. Datapath tests build two hypervisor namespaces, create IPv4 and IPv6 underlay addresses, verify hypervisor reachability, create VM namespaces and bridge/VXLAN mappings, then ping VM pairs. Variants cover inherited remote, per-VNI remote, inherited multicast group, per-VNI multicast group, and a mixed topology with traditional, metadata, and filtering VXLAN devices.

## State and Persistence
The script creates namespaces for hypervisors and VMs, root veth links, bridge devices, VXLAN devices, VLAN subinterfaces, VNI filters, FDB entries, and multicast group joins. `cleanup` removes expected root links and all namespaces after each test. No durable files are written; status is held in shell counters.

## Dependencies and Integration Points
Dependencies are root, `ip`, `bridge`, `ping`/`ping6`, kernel VXLAN external metadata and VNI-filter support, and `lib.sh`. It integrates with bridge VLAN filtering, bridge VLAN tunnel information, VXLAN collect-metadata mode, `bridge vni` netlink API, per-VNI remote/group attributes, VM namespace addressing, and multicast datapath behavior.

## Risks and Test Signals
There are several fragile areas: heavy namespace topology, shell parsing of `vattrs`, old iproute2 behavior, ping timing, and feature interactions with IPv6 multicast. Test signals are explicit API return-code expectations and successful VM pings for IPv4 and IPv6 default remote/group cases plus additional pings for mixed traditional/metadata devices.
