# sources/distributed-fs/glusterfs/xlators/performance/quick-read/src/quick-read-messages.h

Purpose: reserves structured log message IDs for `quick-read`.

Important APIs, types, and functions: `GLFS_MSGID(QUICK_READ, ...)` covers enforcement failures, invalid arguments/config, child/volume misconfiguration, no memory, dict-set failures, and non-empty LRU notices.

Control flow: preprocessor-only; IDs are used by `gf_msg` calls in `quick-read.c`.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must remain aligned with the QUICK_READ component.

Risks and test signals: IDs must be append-only. Build and error-path tests validate use.
