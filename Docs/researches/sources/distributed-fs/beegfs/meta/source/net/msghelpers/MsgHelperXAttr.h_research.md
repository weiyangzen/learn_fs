<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h

## Purpose
Declares static xattr helpers and the socket streaming state object.

## Important APIs, Types, and Functions
`MsgHelperXAttr` exposes `listxattr()`, `getxattr()`, `removexattr()`, `setxattr()`, constants `CURRENT_DIR_FILENAME` and `MAX_VALUE_SIZE`, and nested `StreamXAttrState`. `StreamXAttrState` can be constructed from an `EntryInfo` plus names or from a filesystem path plus names, exposes `streamXattrFn()` for hook registration, and `readNextXAttr()` for receivers.

## Control Flow, State, and Persistence
The nested state stores either an entry pointer or a raw path and a list of names. Its private `streamXattr()` sends the records when invoked by a registered stream-out hook.

## Dependencies and Integration Points
Forward-declares `EntryInfo` and `Socket`; includes storage errors. Used by xattr messages, moving, and mirroring code paths.

## Risks and Test Signals
The `EntryInfo*` in stream state must outlive streaming. Tests should cover both constructors, hook invocation, and receiver interpretation of `SUCCESS` as stream end versus `AGAIN` as record received.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h -->
