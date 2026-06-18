<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go

Purpose: converts BeeMsg structs to/from complete on-the-wire messages containing a serialized header and body.

Important APIs/types/functions: `AssembleBeeMsg` and `DisassembleBeeMsg`.

Control flow: assembly writes a placeholder header, serializes the body, obtains the final buffer from the serializer, then overwrites header message length and feature flags. Disassembly verifies the output target is a pointer, deserializes the header, checks header message ID against `out.MsgId()`, then deserializes the body with header feature flags.

State and persistence: no persistence; transient byte buffers only. Serializer `MsgFeatureFlags` is the bridge from body serialization to header patching.

Dependencies and integration points: depends on `beeserde` and `msg` header helpers. It is called by `WriteTo`, `RequestUDP`, and all TCP/UDP transport paths.

Risks: disassembly assumes callers already split header/body and that buffers contain exactly one message. It does not compare header `MsgLen` to provided body length; length enforcement comes from callers and `beeserde.Finish`.

Test signals: `assemble_test.go` validates round-trip assembly/disassembly and rejects extra/truncated body data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go -->
