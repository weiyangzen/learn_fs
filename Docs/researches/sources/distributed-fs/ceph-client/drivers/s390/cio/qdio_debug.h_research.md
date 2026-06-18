# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_debug.h

Purpose: declares QDIO debug feature globals, logging macros, and debugfs lifecycle hooks.

Important APIs/types/functions: exposes `qdio_dbf_setup`, `qdio_dbf_error`, log levels `DBF_ERR/DBF_WARN/DBF_INFO`, macros `DBF_EVENT`, `DBF_ERROR`, `DBF_DEV_EVENT`, hex helpers, and prototypes for per-device/global debug lifecycle functions.

Control flow: macro calls format bounded 32-byte text events and send them to global or per-device debug feature areas when the requested level is enabled.

State and persistence behavior: the header owns no state except external declarations. Debug output is runtime-only.

Dependencies and integration points: included by QDIO setup, main, thin interrupt, and debug implementation files. Depends on `asm/debug.h`, `asm/qdio.h`, and `qdio.h`.

Risks and test signals: macros evaluate device debug pointers and should only be used after debug areas are initialized. Compile coverage and boot-time QDIO debug initialization are primary validation signals.
