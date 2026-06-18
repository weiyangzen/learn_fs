# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.h

Purpose: private constants for stream2mmio command tokens used by virtual ISYS configuration.

Important definitions: `_STREAM2MMIO_CMD_TOKEN_STORE_PACKETS` and `_STREAM2MMIO_CMD_TOKEN_SYNC_FRAME`.

Control flow/state: no logic or state. `virtual_isys.c` writes these constants into `ibuf_ctrl_cfg.stream2mmio_cfg` as store and sync commands.

Dependencies/integration: tied to stream2mmio hardware command semantics and IBUF controller config.

Risks: the numeric token values are hardware/firmware ABI. Wrong values would desynchronize frame sync or packet storage.

Test signals: config calculation checks that sync/store fields match expected token values and hardware tests confirm frame synchronization and packet capture.
