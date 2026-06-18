# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub-messages.h

Purpose: this header defines structured GlusterFS message IDs and message strings for bit-rot-stub logging. It centralizes stable identifiers for allocation failures, internal xattr protection, bad-object handling, thread lifecycle, quarantine directory errors, and version/signature preparation errors.

Important APIs and definitions: `GLFS_MSGID(BITROT_STUB, ...)` declares all stub message IDs. The `BRS_MSG_*_STR` macros provide human-readable text for specific IDs. Message names include `BRS_MSG_BAD_OBJECT_ACCESS`, `BRS_MSG_NON_BITD_PID`, `BRS_MSG_NON_SCRUB_BAD_OBJ_MARK`, `BRS_MSG_SET_INTERNAL_XATTR`, `BRS_MSG_BAD_OBJECT_DIR_*`, and `BRS_MSG_VERSION_PREPARE_FAIL`.

Control flow role: implementation files use these IDs in `gf_smsg` calls at all critical failure and policy enforcement points. They do not alter behavior, but they make errors searchable and stable across releases.

State and persistence behavior: none directly. The header comments warn that IDs must not be removed to avoid reuse, which is a logging ABI constraint.

Dependencies and integration points: depends on `glfs-message-id.h` and the component name registry. Logs emitted with these IDs are integration points for support tooling, tests that inspect logs, and operational diagnostics.

Risks: adding IDs in the middle or deleting old IDs can break log interpretation. Some string macros are not necessarily used at every call site, so dead message strings can remain for compatibility.

Test signals: compile with all message IDs, run negative tests for internal xattr operations, bad-object access, non-bitd signature attempts, non-scrubber bad-object marks, and quarantine directory failures, then verify structured message IDs are emitted.
