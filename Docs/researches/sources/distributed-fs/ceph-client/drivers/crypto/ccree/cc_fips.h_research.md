<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h

Purpose: declares the CryptoCell FIPS synchronization interface and provides no-op stubs when kernel FIPS crypto support is disabled.

Important APIs, types, and functions: under `CONFIG_CRYPTO_FIPS`, `enum cc_fips_status` defines the bit values exchanged with TEE through GPR registers: module OK, module error, REE status present, and TEE status present. It declares `cc_fips_init()`, `cc_fips_fini()`, `fips_handler()`, `cc_set_ree_fips_status()`, and `cc_tee_handle_fips_error()`. Without FIPS support, all functions inline to no-ops or success.

Control flow: `cc_driver.c` can call FIPS hooks unconditionally. With FIPS disabled, initialization cannot fail and IRQ/status hooks are inert. With FIPS enabled, the C implementation owns notifier registration, tasklet dispatch, and TEE/REE status writes.

State and persistence behavior: no state in the header. The enum values are part of the hardware/software synchronization contract and must remain stable.

Dependencies and integration points: used by the platform driver and ISR path. It relies on `struct cc_drvdata` visibility from includers and hardware register macros in the implementation.

Risks: stubbed success means non-FIPS builds do not exercise real synchronization paths. Enum values must match firmware expectations; changes can invert OK/error reporting. Call sites must still guard hardware IRQ handling through `CONFIG_CRYPTO_FIPS` where the ISR references FIPS-specific masks.

Test signals: build with `CONFIG_CRYPTO_FIPS=y` and `n`, verify probe succeeds in both modes, and for FIPS builds validate status bit definitions against firmware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h -->
