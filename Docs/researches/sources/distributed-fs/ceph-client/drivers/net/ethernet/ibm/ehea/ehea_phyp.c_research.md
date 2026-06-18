# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.c

Purpose: Implements the eHEA driver's Power hypervisor-call wrapper layer. It packs driver data structures into H_CALL register arguments, retries long-busy calls, logs failures, decodes outputs, maps resource EPAs, and exposes typed helpers for QP/CQ/EQ/MR/port/event operations.

Important APIs and functions: `ehea_plpar_hcall_norets()` and `ehea_plpar_hcall9()` wrap `plpar_hcall_norets()` and `plpar_hcall9()`, retrying up to five times on `H_IS_LONG_BUSY()` and sleeping for the hypervisor-provided delay. Allocation helpers include `ehea_h_alloc_resource_qp()`, `ehea_h_alloc_resource_cq()`, `ehea_h_alloc_resource_eq()`, and `ehea_h_alloc_resource_mr()`. Other helpers query/modify QPs and ports, register queue/MR pages, register shared MRs, disable QPs, free resources, register/deregister broadcast/multicast filters, reset notification events, query adapter attributes, and fetch error data.

Control flow: QMR code calls allocation helpers, then registers pages. Main driver calls port/query/modify helpers during probe, open, link settings, filters, VLANs, QP activation, and reset. All helpers translate C fields into bit-packed H_CALL parameters using `EHEA_BMASK_SET()` and decode outputs back into init attributes, handles, lkeys, page counts, interrupt service tokens, or PHYP status.

State and persistence: The file itself stores no long-lived state. It mutates caller-owned structures such as `ehea_qp_init_attr`, `ehea_cq_attr`, `ehea_eq_attr`, and `ehea_mr`, and maps EPAs into `struct h_epas`. Firmware resources persist in the hypervisor until freed by matching calls.

Dependencies and integration: Depends on `asm/hvcall.h`, `plpar_hcall*`, PHYP H_CALL numbers, `ehea_phyp.h` control block definitions, `ehea_hw.h` EPA mapping helpers, and `ehea.h` attributes. It is the only eHEA layer that should know exact register argument packing for PHYP calls.

Risks: Argument packing errors can allocate unusable resources or modify the wrong port/QP state. Long-busy retry is bounded; persistent busy returns `H_BUSY` to callers. Some `H_AUTHORITY` errors for port speed/jumbo/promisc-like operations are intentionally not logged as generic failures. `hcp_epas_ctor()` mapping relies on returned physical addresses and page alignment behavior.

Test signals: Resource allocation/free for EQ/CQ/QP/MR, page registration completion status (`H_PAGE_REGISTERED` then `H_SUCCESS`), QP state transitions, port query/modify authority failures, BCMC register/deregister, long-busy retry behavior, and H_CALL failure logging with useful arguments.
