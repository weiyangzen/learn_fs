# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_regs.h

Purpose: Defines KCR/PXP MMIO register offsets and bits.

Important APIs/types: `GEN12_KCR_BASE`, `MTL_KCR_BASE`, `KCR_INIT()`, `KCR_INIT_ALLOW_DISPLAY_ME_WRITES`, `KCR_SIP()`, and `KCR_GLOBAL_TERMINATE()`.

Control flow: No code. Macros parameterize base address differences between legacy and media-tile KCR.

State/persistence: Hardware registers track display/ME write permission, session-in-play bits, and global termination trigger.

Dependencies/integration: Used by PXP lifecycle and session code through uncore MMIO accessors.

Risks: Wrong base selection causes writes to the wrong MMIO block. Global terminate and session-in-play register use must be under appropriate runtime PM/uncore access.

Test signals: PXP hardware init toggles `KCR_INIT`; session wait polls `KCR_SIP`; teardown writes `KCR_GLOBAL_TERMINATE`.
