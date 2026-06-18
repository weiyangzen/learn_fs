# sources/distributed-fs/ceph-client/drivers/xen/mem-reservation.c

Purpose: provides helper routines for changing Xen memory reservations and, on PV MMU systems, updating or clearing virtual mappings when pages are removed from or returned to the guest reservation.

Important APIs/functions: exports `xen_scrub_pages`, `__xenmem_reservation_va_mapping_update`, `__xenmem_reservation_va_mapping_reset`, `xenmem_reservation_increase`, and `xenmem_reservation_decrease`.

Control flow: PV mapping update sets p2m entries and installs machine-frame PTEs with `HYPERVISOR_update_va_mapping`; reset clears the VA mapping and invalidates the p2m entry. Reservation increase uses `XENMEM_populate_physmap` over PFN extents, while decrease uses `XENMEM_decrease_reservation` over GFN extents. Extent order is chosen so one Linux page maps to the right number of Xen pages.

State and persistence: only the read-mostly `xen_scrub_pages` core parameter is stored here. Reservation calls mutate Xen-owned guest memory reservation and arch p2m/VA mappings through hypercalls.

Dependencies and integration: used by grant-table DMA allocation to temporarily remove DMA pages from the guest reservation and restore them later. Depends on Xen memory hypercalls, page/PFN/GFN conventions, and PV MMU support when compiled.

Risks: callers must pass PFNs to populate and GFNs to decrease; PV MMU assumes Xen and Linux page sizes match; update/reset use BUG_ON for hypercall failures; partial reservation changes must be handled by callers.

Test signals: exercise grant DMA page allocation/free, PV mapping reset/update paths, scrub-pages boot parameter behavior, and failure handling for partial populate/decrease reservation hypercalls.
