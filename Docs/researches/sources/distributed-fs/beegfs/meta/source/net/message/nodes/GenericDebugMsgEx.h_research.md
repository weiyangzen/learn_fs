<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h

Purpose: Declares the GenericDebugMsgEx server-side message extension: server-side generic debug command dispatcher for metadata nodes, including live diagnostics and guarded metadata inspection/mutation commands.

Important APIs/types/functions: Declarations/types: class GenericDebugMsgEx : public GenericDebugMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GenericDebugMsg.h>, <common/Common.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers.

Risks and test signals: Because some commands mutate dentries or inode fields, operational exposure and argument validation are the main risks; tests should exercise malformed command strings and release every referenced inode or directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.h -->
