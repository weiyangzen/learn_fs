## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_data.h

Purpose: Publishes Gen4 hardware constants, register offsets, service/ring topology constants, VF migration private state, and hardware helper prototypes.

Important APIs/types: Defines Gen4 BAR ids, KPT heartbeat frequency, fuse offsets, accelerator counts, MSI-X routing offsets, ring/bank counts, arbiter/admin offsets, default ring-to-service map, watchdog values, ring reset/drain registers, coalescing timeout constants, ERRSOU/ERRMSK offsets, rate-limiting offsets, PF2VM/VM2PF register layout, `struct adf_gen4_vfmig`, Gen4 slice mask enum, RP group enum, and prototypes for Gen4 helpers.

Control flow/state: The header defines MMIO address formulas and `adf_gen4_vfmig` state (`mstate_mgr`, per-bank stopped flags) used by migration. Runtime state is owned by callers and implementation files.

Dependencies/integration: Included by Gen4 config, PFVF, PM, RAS, VF migration, and product-specific hardware data code.

Risks and test signals: Offset and topology constants are high blast-radius. Tests should cover SR-IOV bank mapping, PF/VF mailbox offsets, MSI-X routing, rate-limiting access, ring drain/reset, heartbeat, and VF migration bank counts.
