# sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.h

Purpose: public utility header for the Broadcom SPU crypto driver. It declares utility helpers and defines debug logging macros that compile to active packet/flow logging only under `DEBUG`.

Important APIs and types: external debug controls `flow_debug_logging`, `packet_debug_logging`, and `debug_logging_sleep`; macros `flow_log`, `flow_dump`, `packet_log`, `packet_dump`, and `dump_sg`; prototypes for scatterlist helpers, counter increment, `do_shash()`, `spu_alg_name()`, debugfs setup/teardown, and `format_value_ccm()`.

Control flow: implementation files include this header and use logging macros inline. With `DEBUG` defined, logs check runtime flags, print or hex dump, and optionally sleep; without `DEBUG`, static inline no-op stubs remove the logging cost.

State and persistence: no state is owned here, but the declared debug flags affect global runtime logging and timing.

Dependencies and integration points: includes Linux kernel/delay headers and `spu.h`; bridges utility functions to SPU-M/SPU2 and broader Broadcom driver code.

Risks: enabling debug with `debug_logging_sleep` can materially affect crypto timing and throughput; packet dumps may expose key material because header dump paths print keys and IVs; macro availability depends on compile-time `DEBUG`, not just runtime flags.

Test signals: compile with and without `CONFIG_CRYPTO_DEV_BCM_SPU_DEBUG`/`DEBUG`, verify no-op logging builds, and validate that debugfs/stat helpers are available only through their declarations.
