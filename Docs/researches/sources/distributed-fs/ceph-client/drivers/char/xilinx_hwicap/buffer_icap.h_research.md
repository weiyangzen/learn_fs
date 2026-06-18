<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h

Purpose: Public internal header for the BRAM-buffer HWICAP backend.

Important APIs/types/functions: Declares `buffer_icap_set_configuration()`, `buffer_icap_get_configuration()`, `buffer_icap_get_status()`, and `buffer_icap_reset()` against `struct hwicap_drvdata`.

Control flow: no runtime control flow; it is a compile-time contract used by `xilinx_hwicap.c`.

State and persistence: no state.

Dependencies and integration: includes Linux type/cdev/platform headers, `asm/io.h`, and `xilinx_hwicap.h` for `struct hwicap_drvdata` and shared ICAP constants.

Risks: prototype drift breaks the `hwicap_driver_config` initializer in the common driver. Parameter names use legacy capitalization in comments/prototypes but types match the implementation.

Test signals: compile coverage with `CONFIG_XILINX_HWICAP` catches declaration/definition mismatches; runtime buffer backend tests exercise these exports indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/buffer_icap.h -->
