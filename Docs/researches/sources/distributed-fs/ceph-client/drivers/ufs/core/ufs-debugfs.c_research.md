# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.c

## Purpose

`ufs-debugfs.c` exposes diagnostic and control files under debugfs for UFS host instances: event counters, saved error injection into the error handler, exception-event mask throttling, and TX equalization inspection/retraining controls.

## Important APIs, Types, and Functions

Public functions are `ufs_debugfs_init()`, `ufs_debugfs_exit()`, `ufs_debugfs_hba_init()`, `ufs_debugfs_hba_exit()`, and `ufs_debugfs_exception_event()`. `struct ufs_debugfs_attr` describes file names, modes, and fops. Important handlers include `ufs_debugfs_stats_show()`, `ee_usr_mask_set()`, `ufs_saved_err_write()`, `ufs_tx_eq_params_show()`, `ufs_tx_eqtr_record_show()`, and `ufs_tx_eq_ctrl_write()`.

## Control Flow

Global init creates `/sys/kernel/debug/ufshcd`. Per-HBA init creates a child directory, registers common files, exception event controls, and per-HS-gear TXEQ directories when `UFSHCD_CAP_TX_EQUALIZATION` is set. User writes to `saved_err`/`saved_uic_err` update HBA error fields under `host_lock` and schedule error handling. Exception events may temporarily mask user-enabled exception bits and queue delayed restoration. Writing `retrain` to `tx_eq_ctrl` gates access, resumes runtime PM, and invokes `ufshcd_retrain_tx_eq()`.

## State and Persistence Behavior

State lives in `hba->debugfs_root`, `debugfs_ee_rate_limit_ms`, delayed work, error fields, exception masks, and TXEQ records in `hba->tx_eq_params`. Debugfs state is runtime-only and disappears on driver unload.

## Dependencies and Integration Points

It depends on debugfs, seq_file, runtime PM helpers, UFS error handling, exception event control, and TXEQ helpers in `ufs-txeq.c`. It uses `host_sem` and `ufshcd_is_user_access_allowed()` before device-affecting operations.

## Risks and Test Signals

Risks include debugfs-only writes causing error-handler storms, exception mask restoration races across runtime suspend, file-name-based dispatch mistakes, and TXEQ retraining while the device is not operational. Test signals include debugfs tree creation/removal, stats counter output, saved error writes scheduling EH, exception rate-limit masking/restoration, TXEQ record rendering for invalid/valid gears, and `retrain` denial when access is busy or unsupported.
