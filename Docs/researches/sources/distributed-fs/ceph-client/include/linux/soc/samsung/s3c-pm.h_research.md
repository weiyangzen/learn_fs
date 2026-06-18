# sources/distributed-fs/ceph-client/include/linux/soc/samsung/s3c-pm.h

Purpose: This Samsung S3C header exposes legacy suspend debugging/check helpers and UART save/restore hooks.

Important APIs/types/functions: It defines `S3C_PMDBG`, inline no-op UART save/restore helpers, and optional sleep-debug functions `s3c_pm_check_prepare`, `s3c_pm_check_restore`, `s3c_pm_check_cleanup`, and `s3c_pm_check_store` when sleep debug is enabled; otherwise macros no-op.

Control flow: Legacy S3C PM code prepares checksum/debug state before suspend, restores/checks it after resume, and optionally saves/restores UART state.

State and persistence: Debug check state is maintained by the PM implementation. Hardware UART and memory checksum state are relevant across suspend.

Dependencies and integration: Integrates with Samsung S3C24xx/S3C legacy PM, UART, and debug infrastructure.

Risks and test signals: Debug code must not perturb suspend state. Test with and without sleep debug, UART console after resume, and memory/register checksum reporting.
