# sources/compression/lz4/programs/lz4conf.h

Purpose: compile-time configuration for LZ4 program defaults.

Important macros: `LZ4_CLEVEL_DEFAULT`, `LZ4IO_MULTITHREAD`, `LZ4_NBWORKERS_DEFAULT`, `LZ4_NBWORKERS_MAX`, and `LZ4_BLOCKSIZEID_DEFAULT`.

Control flow/state: preprocessor-only. CLI and I/O code use these macros for default compression level, worker selection/caps, threadpool path selection, and block size.

Dependencies/integration: included by `lz4cli.c`, `lz4io.c`, and `threadpool.c`; intended to be overrideable by build flags.

Risks: POSIX multithread enablement requires pthread build support; high worker caps can create resource pressure; default block size affects frame behavior and tests.

Test signals: build-variant tests and `check_stdvars.sh` protect compile-flag propagation; threaded and frame tests expose bad settings.
