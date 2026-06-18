<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h

Purpose: private pSeries VAS definitions shared by the pSeries VAS implementation and related sysfs/migration code.

Important APIs/types/functions: defines `VAS_MOD_WIN_*` hypervisor modify flags, window status values, user-mode capability bits, GZIP capability descriptors, `enum vas_migrate_action`, `enum vas_cop_feat_type`, hypervisor wire structs `hv_vas_cop_feat_caps` and `hv_vas_win_lpar`, internal `vas_cop_feat_caps`, `vas_caps`, `pseries_vas_window`, and prototypes for sysfs/reconfiguration/migration helpers.

Control flow: this header does not execute logic, but it shapes how `vas.c` interprets capability buffers, tracks credit counters, and records per-window state used by open, close, DLPAR, and LPM flows. Inline stubs return success for migration/DLPAR hooks when `CONFIG_PPC_VAS` is disabled.

State and persistence: the main state model is feature-scoped capability/credit accounting plus a list of open windows. `pseries_vas_window` persists the hypervisor-provided window ID, paste address, fault/completion IRQs, PID, domain, list node, IRQ name, virtual IRQ, and pending fault count for the lifetime of an open file/window.

Dependencies and integration points: includes common `asm/vas.h`, mutex and stringify support, and is consumed by pSeries VAS code and platform migration/DLPAR code. Packed/aligned hypervisor structures are part of the PAPR ABI and must match HCALL buffer layout.

Risks: bit definitions and struct layout are ABI-sensitive. The constants for `VAS_WIN_NO_CRED_CLOSE` and `VAS_WIN_MIGRATE_CLOSE` are not defined here but are expected from common VAS headers; status bit interactions must remain compatible with `vas.c`. Any change to packed structs can break hypervisor communication.

Test signals: compile coverage under `CONFIG_PPC_VAS` and without it, capability query decoding, sysfs output matching hypervisor values, and DLPAR/LPM paths correctly observing the status/credit fields validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas.h -->
