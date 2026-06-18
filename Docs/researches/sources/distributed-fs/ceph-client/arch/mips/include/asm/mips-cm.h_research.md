# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cm.h

Purpose: Coherence Manager (CM) register interface and helper logic for MIPS CPS systems. It must be included through `mips-cps.h`.

Important APIs/types/functions: Externs include `mips_gcr_base`, `mips_cm_l2sync_base`, `mips_cm_phys_base()`, `mips_cm_l2sync_phys_base()`, `mips_cm_is64`, `mips_cm_is_l2_hci_broken`, `mips_cm_error_report()`, `mips_cm_probe()`, and `mips_cm_update_property()`. Accessor macros generate `read_gcr_*`, `write_gcr_*`, `change_gcr_*`, and redirected/core-local variants. Register groups cover GCR config/base/access/revision/errors, L2 sync, GIC/CPC base/status, region masks, L2 cache/prefetch/tag/ECC controls, reset/BEV, core coherence/config/other/reset/id fields. Helpers include `mips_cm_present()`, `mips_cm_has_l2sync()`, `mips_cm_l2sync()`, `mips_cm_revision()`, `mips_cm_max_vp_width()`, `mips_cm_vp_id()`, and locked access to other cores/clusters.

Control flow, state, and persistence: Probe code establishes MMIO bases. Inline helpers conditionally read registers, perform L2 sync via MMIO write, compute VP IDs, and route redirected register windows under locks. Persistent state is hardware CM configuration and exported base pointers.

Dependencies and integration: Depends on CPS accessors, bitfield helpers, CPU topology, and optional `CONFIG_MIPS_CM`. It integrates with cache coherency, SMP bring-up, GIC/CPC discovery, L2 operations, and device-tree properties.

Risks and test signals: Mixed 32/64-bit register access through `mips_cm_is64` and redirected-region locking are high risk. Test CM2/CM3/CM3.5 variants, SMP hotplug, L2 sync, GIC/CPC base discovery, and cache error reporting.
