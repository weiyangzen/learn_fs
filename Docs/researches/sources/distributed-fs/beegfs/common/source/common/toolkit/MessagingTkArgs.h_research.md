<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h

Purpose: Defines argument structures for `MessagingTk` request/response helpers.

Important APIs/types: `RequestResponseTarget` stores target ID, mapper/store pointers, optional target states and mirror buddy mapping. `RequestResponseNode` stores node ID/store and optional state/mirror mapping. `RequestResponseArgs` stores resolved node, request/expected response, output response, timeout, logging flags, and optional extra-data callback/context.

Control flow/state/persistence: These are mutable call-context structures; `MessagingTk` fills output state and response fields. No persistence.

Dependencies/integration: Shared by RPC callers and `MessagingTk.cpp`, connecting routing metadata, target state stores, and messages.

Risks/test signals: Raw pointer initialization is critical. Tests should construct minimal and fully populated args, verify output state updates, log-flag suppression, and extra-data callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h -->
