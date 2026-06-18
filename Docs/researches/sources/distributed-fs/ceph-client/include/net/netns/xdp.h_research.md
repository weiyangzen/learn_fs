# sources/distributed-fs/ceph-client/include/net/netns/xdp.h

Purpose: Defines per-network-namespace XDP state.

Important APIs/types/functions: `struct netns_xdp` stores a mutex and hlist of namespace-scoped XDP resources.

Control flow: XDP resource creation/removal takes the namespace mutex and updates the hlist; lookup/enumeration consults the list for namespace-scoped XDP objects.

State and persistence: Runtime per-net mutex-protected hlist state only.

Dependencies/integration: Depends on XDP sockets/core, netdevice receive path, namespace lifecycle, and optional memory accounting.

Risks/test signals: Test concurrent list updates, XSK bind/unbind across namespaces, teardown with active sockets, device unregister, and cleanup of all hlist entries.
