# sources/distributed-fs/ceph-client/drivers/xen/features.c

Purpose: queries Xen feature submaps at boot and publishes them through the global `xen_features` array for the rest of the Xen guest code.

Important APIs/functions: exports `xen_features` and implements `xen_setup_features`. The `chk_required_feature` macro panics when a feature required by modern Linux-on-Xen support is absent.

Control flow: `xen_setup_features` iterates `XENFEAT_NR_SUBMAPS`, calls `HYPERVISOR_xen_version(XENVER_get_features)`, and expands each 32-bit submap into one byte per feature. For PV guests it verifies `XENFEAT_mmu_pt_update_preserve_ad` and `XENFEAT_gnttab_map_avail_bits`.

State and persistence: feature bits are stored in read-mostly global memory for the lifetime of the kernel. There is no dynamic refresh after boot.

Dependencies and integration: used by Xen architecture, MMU, grant-table, and event code through `xen_feature()`. It depends on Xen version hypercalls and `<xen/features.h>` feature numbering.

Risks: failed hypercall reads silently stop feature discovery at the first failing submap; missing required PV features panic; consumers assume feature bits are stable and initialized before use.

Test signals: boot PV and HVM guests against supported and deliberately feature-limited hypervisors, and check required-feature panic paths in PV-only test configurations.
