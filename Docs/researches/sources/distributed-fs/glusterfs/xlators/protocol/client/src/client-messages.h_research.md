# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-messages.h

## Purpose

`client-messages.h` centralizes log message IDs and common message strings for the protocol/client translator. It provides stable `PC_MSG_*` identifiers for structured logging across fop RPCs, fd/reopen handling, handshake, portmap, cache invalidation, leases, lock recovery, and lifecycle errors.

## Important APIs, types, and functions

- `GLFS_MSGID(PC, ...)` declares the client component message IDs. The comments require new IDs to be appended and never removed to avoid ID reuse.
- Message IDs cover timer events, fd context errors, XDR failures, remote operation failures, handshake/version/portmap failures, reconnect events, volume-id mismatch, auth failures, cache invalidation, lease failures, lock contention, reopen, memory allocation, and bad fds.
- `PC_MSG_*_STR` macros provide reusable human-readable text for many IDs, such as XDR decoding failure, failed fop send, child-up delay, SETVOLUME failure, port number errors, remote subvolume errors, strict client protocol violations, and unknown lock types.

## Control flow

The header has no executable flow. It shapes runtime logging by supplying IDs and string constants to `gf_smsg()`, `gf_msg()`, `gf_msg_debug()`, and related logging calls throughout the client xlator.

## State and persistence behavior

The message ID list is a compatibility surface for logs and tooling. It is not persisted as application state, but stable numeric IDs are important for log analysis, alerting, and documentation. The header explicitly forbids removing IDs even if unused.

## Dependencies and integration points

It includes `<glusterfs/glfs-message-id.h>` for `GLFS_MSGID`. The client implementation files include this header and pass IDs to Gluster logging. Downstream integrations include log parsers, support diagnostics, statedump analysis, and any tests that assert specific message IDs.

## Risks and edge cases

- Removing or reordering IDs can silently reuse numeric IDs for unrelated messages.
- Several string macros contain typos or legacy phrasing (`isze`, `Defering`, `reister`), but changing them may affect tests or operational log matching.
- Message macros do not enforce that callers provide the right contextual key/value pairs.
- Duplicated concepts exist across IDs and strings, so new logging should choose the closest existing ID before appending another one.

## Test signals

Build coverage catches missing IDs. Logging tests should verify representative failure paths emit the expected `PC_MSG_*` IDs: XDR decode failure, fop send failure, bad fd, SETVOLUME failure, auth failure, volume-id mismatch, portmap failure, child-up delay, and fd reopen failure.
