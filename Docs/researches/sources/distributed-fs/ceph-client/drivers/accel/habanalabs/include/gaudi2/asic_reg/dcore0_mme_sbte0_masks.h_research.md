# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_sbte0_masks.h

Purpose: Provides bitfield shifts and masks for the DCORE0 MME SBTE0 stream/bus-transfer engine. Fields cover maximum data/metadata size, force miss, ARUSER/ARCACHE attributes, occupancy and inflight controls, protection, interrupts, rate limiter, clock gating, stall, status drop count, and interface valid/ready debug.

Important APIs/types/functions: Exports 48 `DCORE0_MME_SBTE0_*` field constants, including `DCORE0_MME_SBTE0_MAX_SIZE_DATA_SHIFT` (0), `DCORE0_MME_SBTE0_MAX_SIZE_DATA_MASK` (0xFFFF), `DCORE0_MME_SBTE0_MAX_SIZE_MD_SHIFT` (16), `DCORE0_MME_SBTE0_MAX_SIZE_MD_MASK` (0xFFFF0000), `DCORE0_MME_SBTE0_FORCE_MISS_R_SHIFT` (0), and `DCORE0_MME_SBTE0_INTF_RDY_DBG_RDY_MASK` (0xFFFFFFFF). No code is present.

Control flow: There is no executable flow. Callers use the masks with SBTE0 register addresses from companion headers to configure transfer behavior and decode status.

State and persistence behavior: Compile-time constants only; they guide mutation and interpretation of SBTE0 hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with MME data movement, protection setup, rate limiting, and interrupt handling.

Risks: Incorrect ARUSER, protection, or rate-limit bit packing can cause memory access failures or performance stalls. Debug valid/ready masks are full-width and should be read, not blindly written.

Test signals: SBTE transfer tests, interrupt/status decode tests, rate-limiter behavior, protection faults, and readback after masked configuration writes.
