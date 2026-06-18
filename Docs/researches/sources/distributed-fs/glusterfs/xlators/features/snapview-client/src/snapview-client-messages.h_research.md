# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-messages.h

Purpose: centralizes structured message IDs and common message strings for snapview-client logging.

Important APIs/types: `GLFS_MSGID(SNAPVIEW_CLIENT, ...)` reserves IDs for memory failures, inode/fd context failures, dict errors, graph lookup failures, invalid options, special-directory handling, read-only snapshot write attempts, and mem-pool failures. The file also defines string macros such as `SVC_MSG_NORMAL_GRAPH_LOOKUP_FAIL_STR`, `SVC_MSG_INVALID_ENTRY_POINT_STR`, and `SVC_MSG_LINK_SNAPSHOT_ENTRY_STR`.

Control flow/state: no runtime state. The message IDs are referenced by `gf_smsg`/`gf_msg` calls in `snapview-client.c`.

Dependencies/integration: includes `glusterfs/glfs-message-id.h`; comments require appending new IDs and never reusing/removing IDs to preserve log compatibility.

Risks/test signals: changing ID order can break log tooling. Spelling errors in strings are non-functional but visible. Tests should include compile coverage and log-message stability checks when adding new diagnostics.
