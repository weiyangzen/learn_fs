# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-messages.h

Purpose: declares structured log message IDs for snapview-server.

Important APIs/types: `GLFS_MSGID(SNAPVIEW_SERVER, ...)` covers memory/accounting failures, null/stale gfids, snapshot-list refresh, glfs context/handle failures, inode/fd context errors, xattr/listxattr failures, release/open/read/stat/access/readlink failures, credential-setting failures, RPC setup/submission/XDR failures, dict errors, and glfs initialization/logging/volfile-server failures.

Control flow/state: no runtime state. IDs are consumed throughout `snapview-server.c`, `snapview-server-helpers.c`, and `snapview-server-mgmt.c`.

Dependencies/integration: includes `glusterfs/glfs-message-id.h`. The comment requires appending IDs only and preserving old IDs for log compatibility.

Risks/test signals: message ID reordering can break operational tooling. Compile coverage and log assertion tests should catch missing IDs after adding diagnostics.
