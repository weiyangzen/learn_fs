# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/ibuf_ctrl_rmgr.h

Purpose: private data model and limits for the IBUF resource manager.

Important definitions: `MAX_IBUF_HANDLES` 24, `MAX_INPUT_BUFFER_SIZE` 64 KiB, `IBUF_ALIGN` 8, `ibuf_handle_t` with start/size/active, and `ibuf_rsrc_t` with free-region counters and handle array.

Control flow/state: header has no logic; `ibuf_ctrl_rmgr.c` mutates the single global instance.

Dependencies/integration: start addresses are offsets into input-buffer controller memory used by virtual ISYS channel configs.

Risks: static limits are hardware/protocol assumptions. The type has no owner/stream metadata, so double-release or wrong-address release cannot be reported except by no-op behavior.

Test signals: capacity boundary tests, zeroed init state, handle reuse expectations, and compatibility with maximum calculated virtual ISYS IBUF allocation size.
