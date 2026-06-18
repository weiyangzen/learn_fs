<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c

Purpose: coordinates FIPS status between the REE driver and TEE firmware on CryptoCell hardware that supports GPR0 FIPS synchronization. It reports REE self-test failures to TEE and handles TEE-reported cryptographic failures.

Important APIs, types, and functions: private `struct cc_fips_handle` stores a tasklet, notifier block, and driver pointer. Public functions are `cc_fips_init()`, `cc_fips_fini()`, `fips_handler()`, `cc_set_ree_fips_status()`, and `cc_tee_handle_fips_error()`. Private helpers are `cc_get_tee_fips_status()`, `cc_ree_fips_failure()`, `tee_fips_error()`, and `fips_dsr()`.

Control flow: initialization is a no-op before hardware revision 712. Otherwise it allocates a handle, initializes a tasklet, registers a notifier on `fips_fail_notif_chain`, and immediately checks whether TEE already reported an error. When Linux FIPS infrastructure reports REE failure, `cc_ree_fips_failure()` writes an error status to HOST_GPR0. When the platform ISR sees the GPR0 interrupt, it masks the interrupt and calls `fips_handler()`, which schedules the tasklet. The tasklet checks the stored IRQ bits, calls `cc_tee_handle_fips_error()`, and attempts to unmask the interrupt. Teardown unregisters the notifier, kills the tasklet, and clears the handle.

State and persistence behavior: `drvdata->fips_handle` persists while the device is active. TEE/REE status is exchanged through hardware GPR registers rather than files. The driver may panic if TEE reports failure while the kernel is in FIPS mode; otherwise it logs an error.

Dependencies and integration points: depends on Linux FIPS notifier infrastructure, tasklets, and register access helpers from `cc_driver.h`. `cc_driver.c` initializes FIPS before algorithm allocation completes, calls `cc_set_ree_fips_status(true)` after successful crypto registration, and dispatches GPR0 IRQs into `fips_handler()`.

Risks: FIPS behavior is high impact: a TEE error can intentionally panic the system when `fips_enabled` is true. The tasklet unmask calculation uses register constants and IRQ bits, so it should be reviewed carefully against the intended HOST_IMR read-modify-write behavior. Missing notifier unregister or tasklet kill can race during driver remove. Hardware revision gating must match GPR register availability.

Test signals: boot with `CONFIG_CRYPTO_FIPS=y` and FIPS mode enabled/disabled, inject REE notifier failures, simulate TEE status OK/error bits, verify HOST_GPR0 writes, verify GPR0 interrupt mask/unmask behavior, and remove the device while no tasklet remains scheduled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c -->
