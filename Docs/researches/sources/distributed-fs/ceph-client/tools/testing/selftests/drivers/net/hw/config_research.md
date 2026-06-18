# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/config

Purpose: Kernel config fragment for hardware network driver selftests.

Important entries: BPF syscall, fault injection, ESP/IPsec offload for IPv4/IPv6, io_uring, IPv6/GRE, net classifier/action/BPF, netkit, ingress qdisc, udmabuf, VXLAN, and XFRM user support.

Control flow: No executable flow; declares kernel features required by tests in `hw/`.

State and persistence: Build/test configuration only.

Dependencies and integration points: Enables feature families used by `devmem.py`, `ncdevmem.c`, `iou-zcrx`, IPsec/VXLAN offload, TC tests, XDP/BPF metadata tests, and fault injection tests.

Risks and test signals: Missing entries cause tests to skip, fail at setup, or omit generated helper functionality.
