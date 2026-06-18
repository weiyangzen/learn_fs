# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_ctrl_lo_masks.h

Purpose: Supplies shift and mask constants for the DCORE0 MME low-control register block. It describes bitfields for architecture status, command control, sync-object FIFO thresholds, logging shadows, redundancy, EUS rollup/protection, PCU rate limiting, dummy values, EU/SBTE controls, counters, debug words, and ETF memory wrap fields.

Important APIs/types/functions: Exports 302 `DCORE0_MME_CTRL_LO_*_{SHIFT,MASK}` constants rather than MMIO addresses. Representative fields include `DCORE0_MME_CTRL_LO_ARCH_STATUS_AGU_IN_SHIFT` (0), `DCORE0_MME_CTRL_LO_ARCH_STATUS_AGU_IN_MASK` (0x1F), `DCORE0_MME_CTRL_LO_ARCH_STATUS_EU_SHIFT` (5), `DCORE0_MME_CTRL_LO_ARCH_STATUS_EU_MASK` (0x20), `DCORE0_MME_CTRL_LO_ARCH_STATUS_AP_SHIFT` (6), and `DCORE0_MME_CTRL_LO_ETF_MEM_WRAP_RM_V_MASK` (0x3FFFFFFF).

Control flow: There is no code. Register accessors use these constants to pack writes and unpack reads for the companion `dcore0_mme_ctrl_lo_regs.h` address macros.

State and persistence behavior: The header has no state. Correct use determines how software mutates or interprets persistent hardware state in the MME low-control block.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It is tightly coupled to the generated address header and any debug, reset, or performance logic that decodes MME state.

Risks: A stale mask paired with a newer address map can corrupt unrelated bits. Several fields govern clock gating, rate limiting, error handling, and protection, so read-modify-write discipline is required.

Test signals: Compile checks for macro availability, register bitfield encode/decode unit tests where available, hardware register readback after masked writes, and MME error-injection or performance-counter tests.
