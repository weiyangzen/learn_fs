# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.h

## Research
`GetTargetMappingsRespMsg.h` declares a receive-only target mapping response. It embeds `NetMessage`, owns a `struct list_head mappings` containing `TargetMapping` elements, initializes the list, and relies on the `.c` release hook for cleanup.

Control flow is initialization, deserialization, caller iteration, and message free. State is list-owned deserialized mapping elements. Dependencies include `NetMessage.h` and `Common.h`; the concrete mapping type comes from `Types.h` through serializers. Integration points are the `TargetMapper` that maps storage target IDs to node numeric IDs. Risks are absent serialization support, lifetime mistakes around the list, and not handling duplicate target IDs in the consumer. Test signals are management mapping responses and correct downstream target selection.
