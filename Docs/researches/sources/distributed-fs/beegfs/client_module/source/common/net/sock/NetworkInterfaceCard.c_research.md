# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.c

Purpose: Discovers usable TCP and RDMA NIC addresses for the BeeGFS client module.

Important APIs/types/functions: `NIC_findAll`, `__NIC_findAllTCP`, `__NIC_filterInterfacesForRDMA`, `NIC_nicTypeToString`, `NIC_nicAddrToString`, `NIC_supportsRDMA`, and `NIC_supportedCapabilities` populate `NicAddressList` entries after applying `NicAddressFilter`.

Control flow: The code walks kernel `net_device` entries, skips loopback devices, records IPv4 as mapped IPv6, records only acceptable global-ish IPv6 unicast addresses, then optionally probes RDMA capability by binding an `RDMASocket` to discovered TCP addresses. `onlyRDMA` removes non-RDMA entries afterward.

State and persistence behavior: Allocates `NicAddress` entries into caller-owned lists; no persistent global state. RDMA probe sockets are temporary.

Dependencies and integration points: Integrates Linux networking structures, BeeGFS address filters/lists, `RDMASocket`, and `SocketTk` formatting.

Risks: The device walk has a TODO about RTNL locking; interface churn can race discovery. RDMA probing depends on successful bind behavior and memory allocation. IPv6 filtering can exclude temporary/deprecated/link-local addresses intentionally.

Test signals: Validate filtering, IPv4 mapping, IPv6 exclusion rules, RDMA-only pruning, and no leaks on allocation/probe failure.
