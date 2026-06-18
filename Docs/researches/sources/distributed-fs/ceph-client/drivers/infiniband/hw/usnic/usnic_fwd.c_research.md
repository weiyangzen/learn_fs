# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.c

Purpose: forwarding and filter programming shim between usNIC QP groups and Cisco ENIC firmware devcmds.

Important APIs/functions: `usnic_fwd_dev_alloc/free()`, setters for MAC/IP/carrier/MTU, `usnic_fwd_alloc_flow()`, `usnic_fwd_dealloc_flow()`, `usnic_fwd_enable_qp()`, and `usnic_fwd_disable_qp()`. Internal helpers wrap `enic_api_devcmd_proxy_by_index()`, validate device readiness/filter fields, and build ENIC TLV payloads.

Control flow: PF probe allocates a forwarding device from the PF netdev. Notifiers update link/MAC/IP/MTU. QP group creation builds either a usNIC-ID or UDP 5-tuple filter, validates link and IP/port constraints, DMA-allocates TLVs, sends `CMD_ADD_FILTER`, and records the returned flow ID. QP group state transitions call enable/disable devcmds for the selected RQ/WQ resources; teardown sends `CMD_DEL_FILTER`.

State and persistence: `struct usnic_fwd_dev` caches PF netdev, PCI device, lock, MAC, MTU, link state, IPv4 address, and stable name. `struct usnic_fwd_flow` stores firmware flow ID, VF index, and owner forwarding device.

Dependencies and integration: depends on ENIC internal APIs/types (`enic_api.h`, `vnic_devcmd.h`), Linux netdev/PCI, packet constants, and QP group flow setup.

Risks: filter validity depends on current PF IP/link state and can be invalidated by netdev events. `CMD_DEL_FILTER` errors are logged but converted to success because firmware deletion failure is unrecoverable, which can hide leaked filters. TLV allocation uses `GFP_ATOMIC`; pressure can make QP creation fail. Locking is spinlock-based around firmware proxy commands.

Test signals: add/delete filter devcmds, UDP socket filters matching PF IPv4 address, QP enable/disable transitions, link-down rejection, netdev reboot/down cleanup, and fault injection for ENIC command failures.
