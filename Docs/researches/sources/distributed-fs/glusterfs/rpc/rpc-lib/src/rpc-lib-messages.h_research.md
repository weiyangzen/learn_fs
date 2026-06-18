## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-lib-messages.h

Purpose: reserves structured message IDs for the RPC library component.

Important definitions: uses `GLFS_MSGID(RPC_LIB, ...)` to define transport-related message IDs such as address-family errors, DNS resolution failure, listen/connect path errors, port bind failure, transport errors, timeout exceeded, and socket bind errors.

Control flow: no runtime code. The macro expands into enum/message-id definitions through `glfs-message-id.h`.

State and persistence: message IDs are stable diagnostic ABI. Comments explicitly require appending new IDs and never removing existing IDs to prevent reuse.

Dependencies and integration: included by RPC transport or related code that logs structured messages. Tied to the `RPC_LIB` component registered in `glfs-message-id.h`.

Risks: renumbering or removing IDs breaks log consumers and support tooling. Adding messages in the middle can reuse IDs incorrectly.

Test signals: compile checks and static review ensuring new IDs append only.
