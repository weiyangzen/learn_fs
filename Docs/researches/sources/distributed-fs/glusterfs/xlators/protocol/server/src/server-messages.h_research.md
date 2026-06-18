# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-messages.h

## Purpose

`server-messages.h` declares the protocol/server component's stable GLFS message IDs and message string constants used by logging across server, handshake, helper, auth, resolution, and FOP code.

## Important APIs, types, and functions

The `GLFS_MSGID(PS, ...)` block enumerates all protocol/server message identifiers, including authentication errors, GFID resolution failures, memory/fd errors, uid/gid mapping errors, config issues, connection and cleanup messages, per-FOP trace messages, serialization failures, RPC setup/reconfigure messages, child status, active lock operations, and login/password errors. The `PS_MSG_*_STR` defines provide human-readable strings for many of those IDs.

## Control flow

Source files include this header and pass IDs to `gf_msg()`, `gf_smsg()`, or related logging macros. Message IDs are intentionally append-only to avoid reusing numeric identifiers in logs and tooling.

## State and persistence behavior

No runtime state exists here. The persisted contract is the stable mapping of message ID names to generated numeric IDs through `glfs-message-id.h`.

## Dependencies and integration points

The header depends on `<glusterfs/glfs-message-id.h>`. It integrates with all protocol/server logging and with external log parsers or diagnostics that rely on stable message IDs.

## Risks and test signals

The header explicitly warns never to remove IDs. Risks include renumbering, deleting, or reusing IDs, misspelled constants becoming public API, and string constants drifting from actual log behavior. Build tests catch missing symbols; log-format tests and operational diagnostics catch semantic drift.
