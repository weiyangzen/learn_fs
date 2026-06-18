## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.c

Purpose: Enables Gen4 power management and handles PM interrupts through deferred work.

Important APIs/functions: `adf_gen4_enable_pm()` initializes firmware PM via `adf_init_admin_pm()`, initializes debugfs PM data, enables idle/throttle interrupt bits, clears PM status bits, and unmasks PM in `ERRMSK2`. `adf_gen4_handle_pm_interrupt()` filters for unmasked PM source in `ERRSOU2`, masks PM interrupts, captures `PM_INTERRUPT`, allocates `adf_gen4_pm_data`, and queues `pm_bh_handler()`. `send_host_msg()` sends `PM_SET_MIN` or `PM_NO_CHANGE` based on `ADF_PM_IDLE_SUPPORT` config and polls for firmware to clear the pending bit.

Control flow and state: Interrupt top-half work is minimal and allocates per-event work data. Bottom-half work increments counters in `accel_dev->power_management`, sends host idle acknowledgement/nack, clears PM interrupt status, unmasks PM, and frees work data. Persistent state consists of PM counters and the debugfs print callback installed elsewhere.

Dependencies/integration: Depends on PM CSRs from `adf_gen4_pm.h`, admin PM initialization, config lookup, the miscellaneous workqueue, and Gen4 ERRSOU/ERRMSK constants.

Risks and test signals: `kzalloc(GFP_ATOMIC)` failure causes the handler to return false after masking PM, which is a notable risk. Tests should exercise idle/throttle/fw interrupts, idle-support config parsing defaults, host message busy/timeout, workqueue execution, and PM interrupt re-enable after bottom-half completion.
