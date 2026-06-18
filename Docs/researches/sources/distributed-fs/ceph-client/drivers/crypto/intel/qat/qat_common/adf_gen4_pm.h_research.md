## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pm.h

Purpose: Defines Gen4 power-management registers, bit masks, host-message payloads, and public PM functions.

Important APIs/types: `enum qat_pm_host_msg` has `PM_NO_CHANGE` and `PM_SET_MIN`. The header defines PM host message/status/interrupt offsets, ERRSOU2 PM source, interrupt enable/status bits, pending/payload masks, idle filter defaults, PM debug field masks, and active/managed SSM slice count masks. Declares `adf_gen4_enable_pm()` and `adf_gen4_handle_pm_interrupt()`, plus debugfs `adf_gen4_init_dev_pm_data()` or an inline no-op.

Control flow/state: No state is stored. The masks are consumed by PM enable, interrupt handling, and PM debugfs formatting.

Dependencies/integration: Included by Gen4 PM, PM debugfs, and Gen4 hardware power-up code.

Risks and test signals: Register mask drift can break PM interrupt handling or debugfs decoding. Tests should cover PM enabled with and without debugfs and verify decoded PM status fields against known firmware data.
