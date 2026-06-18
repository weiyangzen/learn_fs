# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.hh

Purpose: Declares the metadata deserialization facade used by QuarkDB services and metadata objects.
Important APIs/types/functions: `Serialization::deserializeFile`, `deserializeContainer`, non-throwing overloads for file/container protobufs and `int64_t`, plus templated `deserialize(const char*, size_t, T&)`.
Control flow: callers can choose exception-based wrappers or `MDStatus` returns. The template wraps raw memory in an `eos::Buffer` and dispatches to the matching overload.
State/persistence: stateless; its contract is the persisted buffer format and type-specific decoding.
Dependencies/integration: forward-declares protobuf types, includes `MDException` and `Buffer`, and depends on implementation checksumming/parsing.
Risks: the template uses `setDataPtr((char*)str, len)`, so callers must ensure the pointed memory outlives deserialization and is compatible with `Buffer` ownership semantics; only explicitly overloaded types are supported.
Test signals: disabled metadata serialization tests document intended coverage; active tests indirectly exercise deserialization when services reload metadata after `shut_down_everything()`.
