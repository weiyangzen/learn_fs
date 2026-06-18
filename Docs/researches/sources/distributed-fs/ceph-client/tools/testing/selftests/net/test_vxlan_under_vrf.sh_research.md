# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_under_vrf.sh

## Purpose
`test_vxlan_under_vrf.sh` checks that VXLAN underlay devices continue to work when moved into a non-default VRF. It simulates two hypervisors and two VMs, verifies VM-to-VM overlay connectivity before the VRF move, moves both underlay `veth0` interfaces into a VRF, bounces the VXLAN devices, and verifies connectivity again.

## Important APIs, Functions, and Types
The script sources `lib.sh`, uses `set -e`, and defines `cleanup`, `setup-hv-networking`, and `setup-vm`. It uses `ip link add type vrf`, `ip link set ... vrf`, Linux bridges, VXLAN links bound to `dev veth0`, veth pairs, `bridge fdb add`, and `ping`.

## Control Flow
The script cleans any stale topology and supports a `clean` argument that exits after cleanup. It creates four namespaces: `hv_1`, `hv_2`, `vm_1`, and `vm_2`. A veth pair connects the hypervisors. Each hypervisor gets `vrf-underlay`, underlay address `172.16.0.x/24`, bridge `br0`, and `vxlan0` attached to the bridge. It confirms hypervisor underlay reachability, then creates a VM veth pair per side and connects each VM to its hypervisor bridge. Static flood FDB entries point each VXLAN device at the other hypervisor. A VM ping verifies default VRF operation. Then both underlay links are enslaved to `vrf-underlay`, both VXLAN devices are brought down/up, and a second VM ping verifies VRF underlay operation.

## State and Persistence
State is transient namespaces, root-namespace veth endpoints during construction, hypervisor bridges, VXLAN links, VRF devices, VM veth interfaces, addresses, and FDB entries. Cleanup deletes known root veth names and all namespaces. No persistent files are created.

## Dependencies and Integration Points
Dependencies include root, `ip`, `bridge`, `ping`, VRF kernel support, VXLAN support, and `lib.sh`. Integration points are VXLAN underlay device binding, VRF master changes, route table association through `type vrf table 1`, bridge/FDB forwarding, and namespace-based topology emulation.

## Risks and Test Signals
The script is intentionally direct and uses `set -e`, so any failed setup command aborts. Risks include kernel or iproute2 lack of VRF/VXLAN support and timing around link rebounce. Test signals are the printed `[ OK ]` checks for hypervisor connectivity, VM overlay connectivity in the default VRF, and VM overlay connectivity after the underlay enters the VRF.
