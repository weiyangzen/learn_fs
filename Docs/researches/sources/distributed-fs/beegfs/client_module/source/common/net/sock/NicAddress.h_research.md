# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddress.h

Purpose: Defines the BeeGFS network-address record and NIC capability enum.

Important APIs/types/functions: `NicAddrType_t` distinguishes standard TCP and RDMA addresses, `NicAddress` stores IPv6-form address, NIC type, interface name, and optional RDMA device pointer, `NicListCapabilities` reports RDMA support, and `NicAddress_equals` compares address/type/name.

Control flow: The equality helper is pure and is used by list comparison and discovery code. RDMA-specific `ibdev` data exists only under `BEEGFS_RDMA`.

State and persistence behavior: Values are copied into list nodes and stats records; no global persistence.

Dependencies and integration points: Used by NIC discovery, connection pools, RDMA sockets, address filters, and priority stats.

Risks: Equality ignores the RDMA `ibdev` pointer, so two otherwise identical RDMA entries compare equal even if device pointers differ. Interface names are fixed-size `IFNAMSIZ` arrays.

Test signals: Compare IPv4-mapped/IPv6 addresses, names, type mismatches, and RDMA builds with/without device pointers.
