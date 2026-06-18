# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.c

Purpose: RDMA verbs callbacks for usNIC's userspace-oriented UD QP model.

Important APIs/functions: `min_transport_spec`, link/query callbacks, `usnic_ib_alloc_pd()/dealloc_pd()`, `usnic_ib_create_qp()/destroy_qp()/modify_qp()/query_qp()`, no-op CQ create/destroy, `usnic_ib_reg_mr()/dereg_mr()`, ucontext alloc/dealloc, and `usnic_ib_mmap()`. Helpers fill create-QP responses, choose VFs, and validate user create-QP transport data.

Control flow: query callbacks synthesize capabilities from PF/VF resource counts, forwarding state, firmware string, and MAC/IP-derived GID. PD allocation creates a UIOM IOMMU domain. Create QP accepts only userspace UD QPs, copies a `usnic_ib_create_qp_cmd`, validates transport, computes required CQ resources, finds a used VF in the same PD when sharing is enabled or an unused VF otherwise, creates a QP group, returns BAR/resource indices, and links the group to the ucontext. Modify QP only handles port validation and QP state changes via QP group modify. MR registration pins/maps user memory through UIOM and returns zero lkey/rkey because userspace owns the datapath. Mmap maps the selected VF BAR0 by VF ID in `vm_pgoff`.

State and persistence: PDs hold `usnic_uiom_pd`; MRs hold `usnic_uiom_reg`; ucontexts are linked into PF context lists and own QP group lists; QP groups persist in context lists until destroyed.

Dependencies and integration: depends on RDMA/uverbs, QP group, vNIC resources, forwarding, transport, UIOM, and MAC/IP-to-GID helpers.

Risks: only UD QPs are supported; unsupported CQ operations are accepted as no-ops except flags. Create-QP response exposes BAR bus address/length and fixed resource arrays. VF sharing relies on UIOM device-list snapshots and freeing them in every path; one success path intentionally hands ownership to the QP group. `query_device()` rejects non-empty udata, which can surprise newer userspace probing extensions.

Test signals: uverbs ABI compatibility, QP creation for custom RoCE and UDP transports, VF sharing on/off, BAR mmap by VF ID and length validation, MR pin/map/release, query outputs across link/IP changes, and destroy/modify state transitions.
