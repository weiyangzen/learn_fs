## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_debug.h

Purpose: provides debug feature levels and convenience macros for AP bus logging through s390 debugfs/debug feature infrastructure.

Important APIs/types/functions: defines `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, `DBF_DEBUG`, helper level selectors `RC2ERR()` and `RC2WARN()`, `AP_DBF_MAX_SPRINTF_ARGS`, and macros `AP_DBF()`, `AP_DBF_ERR()`, `AP_DBF_WARN()`, and `AP_DBF_INFO()`. Declares external `debug_info_t *ap_dbf_info`.

Control flow: AP code calls these macros to log formatted events at a severity level into the `ap` debug feature registered by `ap_bus.c`.

State and persistence: owns no state except the external debug handle declaration. Actual debug buffers are initialized and destroyed in AP bus module lifecycle.

Dependencies and integration: depends on `<asm/debug.h>`. Used by `ap_bus.c` and `ap_queue.c` for scan, state-machine, and error diagnostics.

Risks and test signals: risks are use before debug initialization and format argument count exceeding the registered buffer sizing. Test by enabling AP debug output, exercising scan/error paths, and building with/without AP debug options.
