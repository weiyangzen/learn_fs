# sources/distributed-fs/ceph-client/include/net/netns/vsock.h

Purpose: Defines per-network-namespace VSOCK state.

Important APIs/types/functions: `enum vsock_net_mode` distinguishes global and local modes. `struct netns_vsock` stores sysctl header, protected local port, current mode, child namespace mode, child-mode lock state, and guest-to-host fallback flag.

Control flow: VSOCK sysctls and namespace creation choose global/local mode behavior. Port allocation reads/updates `port` under the global vsock table lock. Child namespace mode and fallback controls affect transport selection.

State and persistence: Runtime per-net mode and port allocation controls.

Dependencies/integration: Depends on VSOCK core, transport modules, socket lifecycle, and namespace cleanup.

Risks/test signals: Test global vs local mode transitions, child namespace mode locking, port allocation under concurrent sockets, guest-to-host fallback behavior, sysctl cleanup, and namespace isolation.
