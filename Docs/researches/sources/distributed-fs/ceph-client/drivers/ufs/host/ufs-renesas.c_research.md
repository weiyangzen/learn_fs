# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-renesas.c

## Purpose
`ufs-renesas.c` is the Renesas R-Car UFS platform variant for `renesas,r8a779f0-ufs`. It supplies the SoC-specific PHY/controller initialization sequences, firmware/calibration handling, runtime PM clock bracketing, DMA mask restriction, and debug register dumping needed before the generic UFS core can bring up the link.

## Important APIs, Types, And Functions
The private state is `struct ufs_renesas_priv`, containing optional firmware, a selected `pre_init` function, a one-time `initialized` flag, and eight calibration bytes read from NVMEM. The main variant callbacks are `ufs_renesas_init()`, `ufs_renesas_exit()`, `ufs_renesas_hce_enable_notify()`, `ufs_renesas_setup_clocks()`, `ufs_renesas_set_dma_mask()`, and `ufs_renesas_dbg_register_dump()`.

The file has many small helpers for indirect register access and PHY programming: `ufs_renesas_write_800_80c_poll()`, `ufs_renesas_write_phy()`, `ufs_renesas_set_phy()`, reset indirect writes, timer disable/restore, and compensation/slicer programming. Two pre-init sequences are selected: `ufs_renesas_r8a779f0_es10_pre_init()` fallback and `ufs_renesas_r8a779f0_pre_init()` for firmware plus calibration.

## Control Flow And State
Probe calls `ufshcd_pltfrm_init()` with `ufs_renesas_vops`. `ufs_renesas_init()` allocates private state, sets `UFSHCD_QUIRK_HIBERN_FASTAUTO`, checks SoC revision fallback rules, attempts to load `r8a779f0_ufs.bin`, reads the `calibration` NVMEM cell, and chooses either the calibrated firmware path or the ES1.0 fallback path. HCE enable notification runs the selected pre-init only once, during PRE_CHANGE, then marks `initialized`.

The initialization sequence writes controller vendor registers through `0xd0/0xd4` windows, polls completion bits, temporarily disables timers, applies many PHY indirect settings, optionally writes firmware words into PHY memory, then restores timer state. Runtime state is memory-only and released at driver exit with `release_firmware()`.

## Dependencies And Integration Points
The driver integrates with the platform UFS glue, firmware loader, NVMEM, SoC revision matching, runtime PM, big-endian/local register access helpers, and the generic UFS core. It constrains DMA with a 32-bit coherent mask. Its DT match table covers `renesas,r8a779f0-ufs`.

## Risks And Edge Cases
The pre-init code is register-sequence sensitive and largely opaque; failures may only show as link startup failures. Firmware and calibration failures intentionally fall back to ES1.0 init, which keeps the device usable but may be suboptimal for later silicon. `ufs_renesas_hce_enable_notify()` sets `initialized` even for non-PRE statuses after the first call, so callback ordering from the core matters. Poll failures log errors but helper functions often continue, making hardware bring-up diagnostics dependent on later failures.

## Test Signals
Test on ES1.0/ES1.1 fallback and non-fallback R-Car hardware, with and without firmware and NVMEM calibration. Validate HCE enable is one-shot across error recovery, runtime PM get/put pairing in clock setup, 32-bit DMA mask configuration, link startup after firmware load, and debug dump availability for vendor registers around `0xc0`.
