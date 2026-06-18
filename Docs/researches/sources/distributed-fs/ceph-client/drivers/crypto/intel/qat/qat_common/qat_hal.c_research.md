# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_hal.c

Purpose: provides the low-level hardware abstraction layer used by the QAT firmware loader. It programs accelerator-engine CSRs, resets and starts AEs, writes microstore/uStore words with ECC, initializes local/register state, and abstracts chip-generation differences.

Important APIs and functions: exported/internal entry points include `qat_hal_init()`, `qat_hal_deinit()`, `qat_hal_reset()`, `qat_hal_clr_reset()`, `qat_hal_start()`, `qat_hal_stop()`, `qat_hal_set_pc()`, `qat_hal_wr_uwords()`, `qat_hal_wr_umem()`, `qat_hal_batch_wr_lm()`, `qat_hal_init_gpr()`, `qat_hal_init_wr_xfer()`, `qat_hal_init_rd_xfer()`, and `qat_hal_init_nn()`. Mode setters configure AE context count, next-neighbor mode, local memory mode, and t-index mode.

Control flow: `qat_hal_init()` allocates the loader handle, HAL state, and chip info, then `qat_hal_chip_init()` fills chip-specific CSR offsets, reset masks, authentication flags, SRAM support, uStore size, AE masks, and revision data based on PCI device ID. It clears reset, initializes transfer registers, and clears GPRs for unauthenticated firmware devices. Start either sends FCU start for authenticated chips or enables contexts and wakeup events directly for legacy unauthenticated chips.

State and persistence: persistent loader state lives in `icp_qat_fw_loader_handle`, `chip_info`, and `hal_handle->aes[]`. The file writes device CSRs, AE context status, wakeup/signal events, timestamp registers, uStore, local memory, and SRAM. Temporary microcode execution saves and restores context registers, uStore words, PC, wakeup/signals, LM addresses, and context enables.

Dependencies and integration points: depends on ADF BAR mapping, PCI IDs, QAT UOF types, CSR macros, and firmware-loader handles. `qat_uclo.c` calls these APIs to load UOF/SUOF firmware and initialize symbols. Authenticated devices rely on FCU control/status registers configured here.

Risks: this code is hardware-stateful and timeout-heavy. Several loops use shared retry counters across AEs or return generic `-EFAULT`, making failure localization difficult. Incorrect chip-info selection can program wrong offsets. Microcode execution must restore saved state exactly; missed restoration can corrupt running firmware. Test signals include reset/start success, CSR timeout paths, ECC uword correctness, 4-context versus 8-context register addressing, authenticated versus legacy start behavior, and per-device PCI ID coverage.
