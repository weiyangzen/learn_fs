# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-messages.h

## Purpose
`glusterd-messages.h` defines the append-only structured logging message IDs and selected message strings for the GlusterD component. It lets GlusterD code log with stable identifiers through `gf_msg()` and `gf_smsg()`.

## Important APIs, Types, And Functions
The core macro invocation `GLFS_MSGID(GLUSTERD, ...)` declares a long ordered list of `GD_MSG_*` identifiers covering quorum, peer/brick disconnects, store failures, snapshot operations, management v3 phases, lock errors, handshake/version negotiation, georeplication, rebalance, volume operations, service management, brick validation, bitrot/scrub, NFS-Ganesha, tiering, transport, and many other GlusterD domains. The comments explicitly require new IDs to be appended, never removed, to prevent ID reuse.

The latter part of the file defines string macros such as `GD_MSG_INVALID_ENTRY_STR`, `GD_MSG_DICT_GET_FAILED_STR`, `GD_MSG_BRICK_NOT_FOUND_STR`, `GD_MSG_VOL_NOT_STARTED_STR`, `GD_MSG_CREATE_DIR_FAILED_STR`, `GD_MSG_FILE_OP_FAILED_STR`, and `GD_MSG_DICT_ALLOC_AND_SERL_LENGTH_GET_FAIL_STR`.

## Control Flow
There is no executable control flow. Including this header makes the generated message IDs available to C files. In this subset, hooks, locks, log ops, handshake, and management handlers all use these IDs to identify error, warning, info, debug, and trace messages.

## State And Persistence Behavior
The file influences log compatibility rather than runtime state. Message IDs are effectively part of GlusterD's external observability contract; log parsers, documentation, and support tooling can depend on them being stable.

## Dependencies And Integration Points
It depends on `<glusterfs/glfs-message-id.h>` and must use the `GLUSTERD` component name known by that infrastructure. Every GlusterD C file that emits structured logs includes this header. Message string macros are consumed where a reusable human-readable error phrase is needed.

## Risks
The largest risk is changing ID order or deleting IDs, which can cause the same numeric ID to refer to a different condition across releases. Typographical mistakes in identifiers can become permanent once shipped. Adding a log call with a poorly matched message ID reduces diagnostic value. The file is large and manually maintained, so merge conflicts and duplicate semantic entries are possible.

## Test Signals
Build tests should catch missing or duplicated identifiers at compile time. Review and static checks should enforce append-only changes and component-name correctness. Runtime tests can assert that high-risk paths, such as management v3 lock failures, handshake rejections, hook failures, and log rotation errors, emit the expected structured IDs.
