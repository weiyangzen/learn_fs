# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_uar.c

Purpose: manages mthca user access region (UAR) allocation and table initialization, including mem-free doorbell table setup.

Important APIs/functions: exports `mthca_uar_alloc`, `mthca_uar_free`, `mthca_init_uar_table`, and `mthca_cleanup_uar_table`.

Control flow: allocation takes a UAR index from `dev->uar_table.alloc` and computes the page frame number from PCI BAR2 plus the index. Free returns the index. Table initialization initializes the allocator with firmware-reserved UARs plus one extra reserved slot, then initializes the kernel doorbell table. Cleanup tears down the doorbell table and allocator.

State and persistence: `struct mthca_uar` stores `index` and `pfn`; table state lives in `dev->uar_table.alloc` and `dev->db_tab` for mem-free devices. All state is runtime and tied to device/context lifetime.

Dependencies and integration: provider user context allocation calls `mthca_uar_alloc`; mmap maps the resulting PFN to userspace. QP/CQ/SRQ kernel paths use the driver UAR and DB table. Depends on PCI resource layout and `mthca_memfree.c`.

Risks: PFN calculation assumes BAR2 is the UAR aperture and one page per UAR. Cleanup does not verify no UARs remain allocated. Doorbell table init failure must unwind allocator init.

Test signals: allocate/deallocate user contexts, mmap UAR page, create mem-free QPs/CQs/SRQs using DB records, exhaust UAR allocation, and unload with debug allocator checks.
