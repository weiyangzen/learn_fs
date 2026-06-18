# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_cr_defs_client.h

Purpose: This generated-style register definition header exposes client-visible Rogue control register offsets and bitfield helpers for tiling, screen sizing, anti-aliasing, and macrotile geometry. It is narrow by design: no code paths, no storage, and no functions, only constants that user/kernel command builders use when programming fields later embedded in FWIF command and HWRT data structures.

Important APIs/types/functions: The main exported constants are `ROGUE_CR_TE_AA` and its `Y2`, `Y`, `X`, and `X2` enable/shift/clear masks; `ROGUE_CR_TE_MTILE1` and `ROGUE_CR_TE_MTILE2` X/Y macrotile boundary fields; `ROGUE_CR_TE_SCREEN` tile-space maximum X/Y fields; `ROGUE_CR_PPP_SCREEN` pixel-space maximum X/Y fields; and `ROGUE_CR_ISP_MTILE_SIZE` macrotile dimensions. There are no C types or callable APIs.

Control flow: None. Consumers compose register words by shifting values into these field definitions and masking with the `CLRMSK`/`MASKFULL` constants.

State and persistence behavior: The header itself has no state. Its constants define hardware-visible state that persists only when written to GPU registers or copied into FW-shared structures such as `rogue_fwif_hwrtdata_common`.

Dependencies and integration points: It is independent except for Linux integer macro conventions. It integrates with render target setup, tiler/macrotiler configuration, MSAA setup, and ISP region sizing. The matching kernel driver must keep these constants aligned with the hardware TRM and firmware expectations.

Risks: Incorrect masks or shifts corrupt register programming and can produce bad tiling, wrong screen bounds, MSAA artifacts, or GPU faults. Because this file is client-visible, ABI mismatches can affect userspace command generation. It has no compile-time layout checks.

Test signals: Build coverage catches syntax only. Functional signals are render tests across no-MSAA/2x/4x paths, large and odd framebuffer sizes, macrotile boundary cases, and comparison of generated register words against known-good traces or hardware documentation.
