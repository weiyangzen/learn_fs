<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h

Purpose: Declares the GM DMA buffer pool structure and operations.

Important APIs, types, and functions: `struct bufferpool` stores the free-list head, owning `gm_port`, and configured buffer count. Function declarations cover init, finalize, get, put, and empty checks.

Control flow and state: Header only. Pool instances are process-local runtime state owned by the GM method.

Dependencies and integration points: Includes `gossip`, `quicklist`, and `<gm.h>`. Used by `bmi-gm.c` to manage reusable GM DMA buffers without repeated allocation in hot paths.

Risks and test signals: The API does not encode buffer size or in-use count, so misuse can return foreign buffers or finalize while buffers are checked out. Tests should cover lifecycle and static analysis should verify all checked-out control buffers are returned in callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h -->
