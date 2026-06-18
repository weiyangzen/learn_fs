# sources/distributed-fs/ceph-client/tools/net/ynl/tests/config

Purpose: kselftest kernel configuration fragment for YNL networking tests. It records the minimum modules/features expected by shell wrappers and C tests.

Important entries: enables network namespaces, IPv6, netdevsim, veth, netkit, Open vSwitch, dummy, routing/diagnostic support, and traffic-control qdisc/classifier/action modules such as ingress, fq_codel, flower, vlan action, and generic classifier/action support.

Control flow/state: declarative only; no runtime behavior. Its state affects whether test environments can load modules and create links/qdiscs/routes required by the wrappers.

Dependencies/integration: consumed by the kernel selftest config machinery and mirrors assumptions in `ynl_nsim_lib.sh`, `test_ynl_cli.sh`, `test_ynl_ethtool.sh`, `tc.c`, `rt-link.c`, and route/address tests.

Risks/test signals: missing `CONFIG_NETDEVSIM`, `CONFIG_NET_NS`, or `CONFIG_VETH` causes broad skips/failures. Missing TC modules affects `tc.c`; missing Open vSwitch affects `ovs.c`; missing netkit affects `rt-link.c`. Successful module load and namespace setup are the main early signals.
