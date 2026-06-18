# sources/distributed-fs/ceph-client/net/smc/smc_core.h

## Purpose
`smc_core.h` is the shared contract for the SMC core, SMC-R link, SMC-D group, buffer, token, and initialization structures. It defines the in-memory model consumed by the connection setup, RDMA, LLC, CDC, ISM, diagnostics, and netlink code.

## Important APIs, Types, and Functions
The header defines `struct smc_lgr_list`, `enum smc_lgr_role`, `enum smc_link_state`, WR buffer types, `struct smc_link`, `struct smc_buf_desc`, `struct smc_rtoken`, `enum smc_lgr_type`, `enum smcr_buf_type`, `enum smc_llc_flowtype`, `struct smc_llc_flow`, `struct smc_link_group`, `struct smc_init_info_smcrv2`, and `struct smc_init_info`. Inline helpers include `smc_lgr_find_conn()`, `smc_conn_lgr_valid()`, `smc_link_usable()`, `smc_link_sendable()`, `smc_link_active()`, `smc_link_shared_v2_rxbuf()`, `smc_gid_be16_convert()`, `smc_set_pci_values()`, and `smc_get_lgr()`. It declares exported core lifecycle, buffer, link, rtoken, VLAN, netlink, and termination functions.

## Control Flow
The header does not execute flow itself, but it encodes the control boundaries. `struct smc_init_info` carries CLC negotiation results into `smc_conn_create()`. `struct smc_link_group` unifies SMC-R and SMC-D through a tagged union, so most core code first checks `is_smcd` before interpreting either RoCE link arrays and LLC state or ISM peer/device state. Link state helpers distinguish receive-capable links from fully sendable RTS links, which is important during first contact and link add flows.

## State and Persistence
All fields are transient kernel memory. `struct smc_link_group` persists while refcounted by connections, links, work items, or global/device lists. It stores buffer pools, connection rb-tree, workqueue, delayed free/terminate work, SMC protocol version details, peer identity, SMC-R rtoken table, LLC flow state, and SMC-D peer GID/device state. `struct smc_link` carries QP, CQ-facing WR vectors, DMA addresses, GIDs, QP numbers, PSNs, link IDs, UID fields, work items, and counters.

## Dependencies and Integration Points
The header includes Linux atomics, PCI, RDMA verbs, generic netlink, `net/smc.h`, local SMC, IB, and CLC headers. Its declarations are used by `smc_core.c`, `smc_llc.c`, `smc_ib.c`, `smc_ism.c`, `smc_diag.c`, and netlink code. It also exposes netlink dump entry points consumed by the generic netlink operation table.

## Risks
Because this header centralizes cross-module layout, field changes have broad ABI-like internal impact. The union in `struct smc_link_group` requires strict `is_smcd` checks. Inline link state helpers have subtly different semantics, so using `smc_link_usable()` where `smc_link_sendable()` is required can send on a QP that is not RTS. The buffer descriptor union also requires callers to know whether a descriptor belongs to SMC-R or SMC-D.

## Test Signals
Compile coverage across SMC-R, SMC-D, IPv6, s390, and non-s390 configurations is important. Runtime signals include correct link-group reuse, netlink dumps, link failover, SMC-D DMB handling, SMC-R v2 shared receive buffers, PCI metadata reporting, and no lockdep or KASAN reports around connection and buffer lifetime.
