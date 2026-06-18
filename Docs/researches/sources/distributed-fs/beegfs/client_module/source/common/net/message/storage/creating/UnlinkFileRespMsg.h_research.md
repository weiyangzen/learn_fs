# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `UnlinkFileRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are UnlinkFileRespMsg_init, UnlinkFileRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
