<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h

Purpose: Public internal header for the FIFO HWICAP backend.

Important APIs/types/functions: Declares `fifo_icap_get_configuration()`, `fifo_icap_set_configuration()`, `fifo_icap_get_status()`, `fifo_icap_reset()`, and `fifo_icap_flush_fifo()`.

Control flow: no runtime flow; this header supplies prototypes consumed by the common HWICAP module.

State and persistence: no state.

Dependencies and integration: includes the common `xilinx_hwicap.h` definitions and Linux/IO headers. `xilinx_hwicap.c` uses the declarations to populate `fifo_icap_config`.

Risks: declaration drift breaks the backend config table. `fifo_icap_flush_fifo()` is exported internally but not wired into the generic config vtable, so direct users must include this header.

Test signals: compile the HWICAP module and run FIFO-backend probe/read/write tests to cover the declared functions indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.h -->
