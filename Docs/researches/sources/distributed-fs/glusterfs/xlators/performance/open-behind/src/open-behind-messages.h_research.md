# sources/distributed-fs/glusterfs/xlators/performance/open-behind/src/open-behind-messages.h

Purpose: reserves structured log message IDs and short strings for `open-behind`.

Important APIs, types, and functions: `GLFS_MSGID(OPEN_BEHIND, ...)` defines IDs for child misconfiguration, dangling volume, no memory, failed fop submission, and bad state. Also defines `OPEN_BEHIND_MSG_FAILED_STR` and `OPEN_BEHIND_MSG_BAD_STATE_STR`.

Control flow: preprocessor-only; consumed by `gf_msg`/`gf_smsg` calls in `open-behind.c`.

State and persistence: no runtime state.

Dependencies and integration: includes `<glusterfs/glfs-message-id.h>` and must match the OPEN_BEHIND namespace.

Risks and test signals: log IDs must remain stable and append-only. Compile coverage through error paths validates symbol availability.
