# sources/distributed-fs/ceph-client/include/xen/interface/grant_table.h

Purpose: declares Xen grant table ABI structures, grant entry formats, grant operation command numbers, map/copy/transfer payloads, status codes, and mapping flags. It is the core cross-domain shared-page permission interface used by Xen paravirtual devices.

Important APIs/types/functions: `grant_ref_t`, `grant_handle_t`, `grant_status_t`, `struct grant_entry_v1`, `union grant_entry_v2`, and `struct grant_entry_header` model grant table storage. Operation payloads include `gnttab_map_grant_ref`, `gnttab_unmap_grant_ref`, `gnttab_setup_table`, `gnttab_transfer`, `gnttab_copy`, `gnttab_query_size`, `gnttab_unmap_and_replace`, `gnttab_set_version`, `gnttab_get_status_frames`, `gnttab_get_version`, `gnttab_swap_grant_ref`, and `gnttab_cache_flush`. Flags cover grant types (`GTF_permit_access`, `GTF_accept_transfer`, `GTF_transitive`), access bits (`GTF_readonly`, `GTF_reading`, `GTF_writing`), transfer bits, `GNTMAP_*`, `GNTCOPY_*`, and `GNTTAB_CACHE_*`.

Control flow: guests publish grants by writing `domid` and frame fields, issuing a write barrier, then setting valid flags. Consumers map grants via `GNTTABOP_map_grant_ref`, use returned handles, and release with `GNTTABOP_unmap_grant_ref`. Copies can use grant refs or MFNs, transfers require a receiving grant entry, and version 2 separates status frames for better synchronization.

State and persistence: grant entries are shared pages between Xen and a domain. Some entries are reserved for console and XenStore. Mappings persist until unmapped by handle; transfers have committed/completed handshakes that must be observed.

Dependencies and integration points: includes `xen/interface/xen.h` for domain IDs, PFNs, guest handles, and alignment types. Nearly every Xen IO protocol in this subset depends on grant refs for shared rings or data pages.

Risks: memory ordering and atomic invalidation are security-sensitive. Reusing active grants, unmapping by the wrong handle, leaving stale device mappings, or mishandling version 1 vs 2 frame widths can leak or corrupt cross-domain memory.

Test signals: grant map/unmap stress, concurrent grant invalidation tests, v1/v2 negotiation, copy and transfer error-path coverage, and leak checks showing no outstanding grant handles after frontend/backend disconnect.
