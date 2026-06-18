<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go

Purpose: declares the minimal interfaces that identify BeeGFS messages and connect them to the shared serializer/deserializer contracts.

Important APIs/types/functions: `Msg` requires `MsgId() uint16`; `SerializableMsg` embeds `Msg` and `beeserde.Serializable`; `DeserializableMsg` embeds `Msg` and `beeserde.Deserializable`.

Control flow: no executable flow; these interfaces are compile-time contracts consumed by transport helpers.

State and persistence: none.

Dependencies and integration points: ties `common/beemsg/msg` payloads to `common/beemsg/beeserde`. `util.AssembleBeeMsg`, `DisassembleBeeMsg`, `WriteTo`, `ReadFrom`, `RequestTCP`, `RequestUDP`, and `NodeStore` all depend on these interfaces.

Risks: all protocol correctness is delegated to implementing structs. A wrong `MsgId` compiles but causes runtime mismatch errors or server-side misinterpretation.

Test signals: indirectly exercised by all message, assembly, I/O, and communication tests that use `testMsg` or real message structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go -->
