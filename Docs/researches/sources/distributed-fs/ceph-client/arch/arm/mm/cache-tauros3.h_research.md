# sources/distributed-fs/ceph-client/arch/arm/mm/cache-tauros3.h

Purpose: defines Tauros3-specific L2 cache controller register offsets and control bits used by the L2x0 framework.

Important APIs/types/functions: constants include `TAUROS3_EVENT_CNT2_CFG`, `TAUROS3_EVENT_CNT2_VAL`, `TAUROS3_INV_ALL`, `TAUROS3_CLEAN_ALL`, `TAUROS3_AUX2_CTRL`, and `TAUROS3_AUX2_CTRL_LINEFILL_BURST8_EN`.

Control flow: no executable control flow. `cache-l2x0.c` includes this header to save and restore Tauros3 AUX2 and prefetch registers and to describe the Tauros3 variant as PL310-compatible with extensions.

State and persistence: no state. The constants describe MMIO register layout used to access persistent hardware state in the controller.

Dependencies and integration points: included by `cache-l2x0.c`. Integrates Marvell Tauros3 support into the generic L2x0 controller path.

Risks: wrong register offsets would make save/restore or maintenance target the wrong MMIO registers. The header documents that Tauros3 is PL310 r0p0-compatible but has r2p0-style prefetch control and an extra event counter, so generic PL310 assumptions may not cover all behavior.

Test signals: build Tauros3 configurations, verify `cache-l2x0.c` saves/restores AUX2 and prefetch registers, and compare register offsets with platform documentation or hardware bring-up logs.
