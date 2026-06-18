# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_pd.c

Purpose: allocates and frees mthca protection domains and initializes the PD number allocator.

Important APIs/functions: exports `mthca_pd_alloc`, `mthca_pd_free`, `mthca_init_pd_table`, and `mthca_cleanup_pd_table`. `mthca_pd_alloc` assigns `pd->privileged`, initializes `sqp_count`, allocates a PD number, and for privileged kernel PDs creates a no-translation local read/write MR in `pd->ntmr`.

Control flow: allocation takes a PD index from `dev->pd_table.alloc`. If the PD is privileged, it calls `mthca_mr_alloc_notrans`; failure releases the PD number. Free tears down the privileged notrans MR before returning the PD number. Table init reserves firmware-reserved PDs and caps the allocator at 24-bit PD numbers.

State and persistence: PD state is held in `struct mthca_pd`: `pd_num`, `privileged`, `sqp_count`, and optional `ntmr`. It is runtime-only and tied to RDMA core PD object lifetime.

Dependencies and integration: called by provider `alloc_pd/dealloc_pd`; the privileged MR is used by special QP management send headers and other kernel-only mappings. Depends on the common mthca allocator and MR allocation code.

Risks: privileged PD setup can fail after PD number allocation and must unwind correctly. The cleanup path explicitly does not check for still-allocated PDs. Kernel consumers rely on `ntmr` being valid for special QP header DMA segments.

Test signals: create/destroy user and kernel PDs, create SMI/GSI QPs requiring privileged PD resources, exhaust PD allocation, and probe/unload with leak/debug allocator checks.
