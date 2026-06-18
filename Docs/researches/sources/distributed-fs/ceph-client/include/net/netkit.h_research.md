# sources/distributed-fs/ceph-client/include/net/netkit.h

Purpose: Declares BPF attach/detach/query interfaces for Netkit devices and a peer-device helper.

Important APIs/types/functions: With `CONFIG_NETKIT`, APIs are `netkit_prog_attach`, `netkit_link_attach`, `netkit_prog_detach`, `netkit_prog_query`, and indirect-callable `netkit_peer_dev`. Without Netkit, stubs return `-EINVAL` or `NULL`.

Control flow: BPF syscall paths call attach/link/detach/query functions using `union bpf_attr` and `bpf_prog`. Device-facing code can resolve a peer device through the indirect-callable helper.

State and persistence: Actual attachment and link state lives in Netkit implementation and BPF link/prog objects. Header stubs hold no state.

Dependencies/integration: Depends on Linux BPF types, netdevice internals, indirect-call declarations, and `CONFIG_NETKIT`.

Risks/test signals: Test disabled-config stubs, BPF program/link lifecycle, query correctness, peer-device lifetime, and indirect call target registration.
