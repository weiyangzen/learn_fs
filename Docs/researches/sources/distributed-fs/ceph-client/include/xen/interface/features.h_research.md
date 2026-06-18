# sources/distributed-fs/ceph-client/include/xen/interface/features.h

Purpose: defines the `XENFEAT_*` feature-bit numbers returned by `XENVER_get_features`. The file is a public ABI contract between Xen and guests; it has no runtime code, only stable indexes into the feature bitmap.

Important APIs/types/functions: `XENFEAT_writable_page_tables`, `XENFEAT_auto_translated_physmap`, `XENFEAT_hvm_callback_vector`, `XENFEAT_hvm_safe_pvclock`, `XENFEAT_dom0`, `XENFEAT_memory_op_vnode_supported`, `XENFEAT_ARM_SMCCC_supported`, `XENFEAT_linux_rsdp_unrestricted`, and the direct-map pair `XENFEAT_not_direct_mapped`/`XENFEAT_direct_mapped`. `XENFEAT_NR_SUBMAPS` is `1`, so consumers expect one feature submap here.

Control flow: callers issue the Xen version/features hypercall elsewhere, then test these numeric bits to select page-table update rules, callback delivery, PV clock safety, memory-op behavior, direct mapping assumptions, and architecture-specific boot handling. The deprecated grant identity mapping bit remains commented out and should not be consumed.

State and persistence: feature state is hypervisor-provided and effectively immutable for a running domain. The header itself persists no data.

Dependencies and integration points: consumed by guest arch setup, HVM/PVH boot, grant-table mapping, memory hotplug/placement, and ARM SMCCC paths. It intentionally has no includes beyond guards.

Risks: changing bit numbers breaks ABI. Incorrect fallback for older Xen releases can mis-handle direct-mapped vs translated domains. Feature checks must gate behavior that is not universally supported, especially HVM callback vectors and pvclock use.

Test signals: compile-time inclusion in guest drivers, boot tests on old and new Xen, and runtime probes showing expected feature-bit driven branches for PV, HVM/PVH, x86, and ARM guests.
