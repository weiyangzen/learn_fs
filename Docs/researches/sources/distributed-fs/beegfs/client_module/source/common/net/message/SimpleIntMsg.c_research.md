# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.c

## Research
`SimpleIntMsg.c` implements the shared payload ops for one signed integer. The ops table points to `SimpleIntMsg_serializePayload`, `SimpleIntMsg_deserializePayload`, default incoming processing, and default feature flags. Serialization writes `value` as an int; deserialization reads it and returns success/failure from the serialization layer.

Control flow is intentionally minimal and relies on the base `NetMessage` for header handling. State is one scalar in the message instance and is not persisted. Dependencies are `SimpleIntMsg.h` and `Serialization`. Integration points include many control and response wrappers: node queries by node type, remove-node responses, lock responses, close-file responses, and generic integer result codes. Risks are mapping integer values to different semantic enums without local validation and accidental use for wire fields that require unsigned width. Test signals are round-trip payload tests and derived response handling that converts integers to `FhgfsOpsErr` or node-type values correctly.
