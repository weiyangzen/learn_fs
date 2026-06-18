# subset-b-000518 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/license.pb.cc -->
# sources/distributed-fs/beegfs-protobuf/cpp/license.pb.cc

## Purpose
This file is generated C++ Protocol Buffers implementation code for `license.proto`, produced by protoc 29.2 / Protobuf C++ 5.29.2. It provides the concrete runtime backing for the declarations in `license.pb.h`: file descriptors, default instances, parse tables, constructors/destructors, serialization, byte-size calculation, merging, copying, swapping, and metadata access for the BeeGFS license/certificate schema in namespace `license`.

The source schema is intended to transfer certificate verification and certificate data from a Go license library to consumers through C FFI-friendly protobuf-encoded payloads. The C++ generated implementation is therefore a wire-compatibility artifact shared with the Go output under `go/license/` and Rust output under `rust/license.rs`.

## Important APIs, Types, And Functions
- Static protobuf runtime state: `_VerifyFeatureResult_default_instance_`, `_VerifyCertResult_default_instance_`, `_CertData_default_instance_`, `_GetCertDataResult_default_instance_`, `file_level_enum_descriptors_license_2eproto`, `descriptor_table_protodef_license_2eproto`, `descriptor_table_license_2eproto_deps`, `descriptor_table_license_2eproto_once`, and `descriptor_table_license_2eproto`.
- Descriptor and enum helpers: `VerifyResult_descriptor()`, `VerifyResult_IsValid(int)`, `CertType_descriptor()`, and `CertType_IsValid(int)`. Validity is range-based: `VerifyResult` accepts 0-3 and `CertType` accepts 0-6.
- Class implementations for `VerifyCertResult`, `VerifyFeatureResult`, `GetCertDataResult`, and `CertData`. Each class has generated implementations for `SharedCtor`, `SharedDtor`, copy construction, `Clear`, `_InternalSerialize`, `ByteSizeLong`, `MergeImpl`, `CopyFrom`, `InternalSwap`, `GetClassData`, and `GetMetadata`.
- Generated table-driven parser metadata: `TcParseTable` instances for all four messages. These map field numbers and wire tags to `TcParser` handlers such as `SingularVarintNoZag1`, `FastUS1`, `FastUR1`, and `FastMtS1`.
- `TableStruct_license_2eproto::offsets` and `schemas[]` tie protobuf reflection/migration metadata to concrete C++ object layout offsets for the generated message fields.

## Control Flow
Startup/descriptor flow is static and protobuf-runtime controlled. The compiled-in `descriptor_table_protodef_license_2eproto` embeds the complete `license.proto` descriptor, including the dependency on `google/protobuf/timestamp.proto`, message fields, enum values, Go package option, and the `DNSNames` JSON name override. `descriptor_table_license_2eproto` registers the schema, default instances, layout schemas, offsets, enum descriptor slots, and dependency table. A file-scope `PROTOBUF_ATTRIBUTE_INIT_PRIORITY2` initializer calls `AddDescriptors(&descriptor_table_license_2eproto)`, while descriptor accessors use `AssignDescriptors` on demand.

Construction flow initializes protobuf-owned storage. Scalar fields are zeroed, enum fields start at the unspecified value, strings use `ArenaStringPtr`, repeated DNS names use `RepeatedPtrField<std::string>`, submessages start as null pointers, and explicit-presence submessages are tracked by a `HasBits<1>` bitmap. Copy constructors merge unknown fields, copy arena string/repeated state, deep-copy present submessages via `Message::CopyConstruct`, and memcpy scalar runs where generated layout permits.

Parsing flow is delegated to generated `TcParseTable` metadata. `VerifyCertResult` parses `result`, `serial`, and `message`; `VerifyFeatureResult` parses `result` and `message`; `GetCertDataResult` parses `result`, optional `data`, and `message`; `CertData` parses all 13 fields, including timestamp submessages, repeated `dns_names`, boolean `is_ca`, and recursive optional `parent_data`.

Serialization flow writes only non-default or present fields. Enums and scalar integers are emitted when nonzero; strings are emitted when non-empty after UTF-8 verification; timestamps, `GetCertDataResult.data`, and `CertData.parent_data` are emitted when their has-bits are set; repeated DNS names emit one length-delimited string per element; unknown fields are appended if present. `ByteSizeLong` mirrors this field-presence logic and updates cached sizes through `MaybeComputeUnknownFieldsSize`.

Merge flow follows normal protobuf semantics: singular strings and scalar fields overwrite only when the source value is non-default, repeated `dns_names` append/merge, present submessages are copy-constructed or merged into existing submessages, has-bits are ORed into the destination, and unknown fields are preserved.

## State And Persistence
Persistent state is the protobuf wire form defined by field numbers and enum numeric values. `license.pb.cc` preserves that contract through generated serializers and the embedded descriptor table. The durable schema is:
- `VerifyCertResult`: field 1 `result`, field 2 string `serial`, field 3 string `message`.
- `VerifyFeatureResult`: field 1 `result`, field 2 string `message`.
- `GetCertDataResult`: field 1 `result`, field 2 `CertData data`, field 3 string `message`.
- `CertData`: field 1 `type`, field 2 int64 `serial`, fields 3-8 subject strings, fields 9-10 protobuf timestamps, field 11 repeated `dns_names` with JSON name `DNSNames`, field 12 bool `is_ca`, and optional recursive field 13 `parent_data`.

In-memory state is owned by generated message instances and may live on the heap or a protobuf arena. The implementation maintains unknown fields in `_internal_metadata_`, so newer-wire fields can survive parse/merge/serialize cycles when using the full message runtime. `Clear()` resets user-visible fields and has-bits but generally clears rather than deallocates existing submessage objects, allowing object reuse.

## Dependencies And Integration Points
- Includes and depends on `license.pb.h`, Protobuf generated-message internals, reflection, descriptors, wire-format helpers, coded streams, and `google/protobuf/timestamp.pb.h` through the header.
- The descriptor dependency table references `descriptor_table_google_2fprotobuf_2ftimestamp_2eproto`, so C++ consumers must link the protobuf timestamp generated/runtime support.
- Must match `license.pb.h` exactly; both are generated from `proto/license.proto` and guarded by the Protobuf 5.29.2 runtime/header version check in the header.
- Generated alongside Go and Rust license outputs by `sources/distributed-fs/beegfs-protobuf/Makefile` using `protoc -I proto --cpp_out=cpp proto/*.proto` and `protoc-rs`.
- Cross-repo integration appears in generated management bindings; for example the Rust management output contains a `cert_data: Option<super::license::GetCertDataResult>` field, so this schema can be nested into management-facing responses.

## Risks And Edge Cases
- This is checked-in generated code. Manual edits are fragile: regeneration from `proto/license.proto` will overwrite them, and hand changes can desynchronize C++, Go, and Rust wire contracts.
- The implementation uses Protobuf C++ internal APIs and generated layout details (`TcParseTable`, `ClassDataFull`, `PROTOBUF_FIELD_OFFSET`, `memswap`, `ArenaStringPtr`). These are not stable application APIs and are tied to Protobuf C++ 5.29.2.
- Enum parsing is open at the wire level. The generated field layout marks enum fields as `kOpenEnum`, and setters store integer-backed enum values; callers must not treat deserialized values as semantically valid without application-level validation.
- `CertData.parent_data` is recursively typed. The generated code will handle nested messages, but application inputs can still create very deep issuer chains that stress parse/merge/serialize recursion, memory use, or stack limits enforced by the protobuf runtime.
- Presence and default values are separate for submessages. A present `data`, `valid_from`, `valid_until`, or `parent_data` may be present but cleared/default-valued, which can be semantically different from absent on the wire.
- Ownership-sensitive paths are arena-aware. `SharedDtor` deletes heap-owned submessages, `set_allocated_*` may adopt or copy across arenas, and unsafe arena APIs bypass those checks. Incorrect caller ownership in user code can cause leaks, dangling pointers, or double deletes.
- String serialization verifies UTF-8. Invalid byte sequences in string fields can trigger protobuf runtime verification behavior rather than silently round-tripping as arbitrary bytes.

## Test Signals
- `make test-protos` in `sources/distributed-fs/beegfs-protobuf` is the primary generated-code freshness signal. It regenerates Go, C++, and Rust outputs and fails if any generated file differs from the checked-in state.
- Compile/link tests for C++ users should include both `license.pb.h` and `license.pb.cc` with Protobuf C++ 5.29.2 headers/runtime and timestamp support.
- Round-trip tests should serialize and parse all four messages, including unknown fields, nonzero enum/scalar values, empty/default values, and repeated DNS names.
- Presence tests should verify `GetCertDataResult.data`, `CertData.valid_from`, `CertData.valid_until`, and `CertData.parent_data` remain distinguishable between absent and present/default-cleared states.
- Cross-language tests should compare C++, Go, and Rust encodings for `VerifyCertResult`, `VerifyFeatureResult`, `GetCertDataResult`, and nested `CertData`, especially enum numbers and `DNSNames` JSON naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/license.pb.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/license.pb.h -->
# sources/distributed-fs/beegfs-protobuf/cpp/license.pb.h

## Purpose
This file is the generated C++ Protocol Buffers public header for `license.proto`, produced by protoc 29.2 / Protobuf C++ 5.29.2. It declares the BeeGFS license verification and certificate data API in namespace `license`, including enum domains, message classes, accessors, reflection hooks, arena-aware ownership APIs, unknown-field access, and inline field operations.

The schema is designed to pass certificate verification results and simplified x509 certificate data from a Go license library to consumers in languages that can exchange C strings or protobuf payloads. The header is the C++ compile-time contract for that wire schema.

## Important APIs, Types, And Functions
- Version and descriptor declarations: the header enforces `PROTOBUF_VERSION == 5029002`, declares `TableStruct_license_2eproto`, and exposes `descriptor_table_license_2eproto`.
- Enums:
  - `VerifyResult`: `VERIFY_UNSPECIFIED`, `VERIFY_ERROR`, `VERIFY_VALID`, and `VERIFY_INVALID`, with `VerifyResult_IsValid`, `VerifyResult_descriptor`, `VerifyResult_Name`, and `VerifyResult_Parse`.
  - `CertType`: `CERT_TYPE_UNSPECIFIED`, `CERT_TYPE_CA_ROOT`, `CERT_TYPE_CA_INTERMEDIATE`, `CERT_TYPE_PARTNER`, `CERT_TYPE_ENTERPRISE`, `CERT_TYPE_TRIAL`, and `CERT_TYPE_COMMUNITY`, with equivalent descriptor/name/parse helpers.
- `VerifyCertResult final : google::protobuf::Message`: result of certificate verification. Public field API covers `result` field 1, string `serial` field 2, and string `message` field 3.
- `VerifyFeatureResult final : google::protobuf::Message`: result of feature verification. Public field API covers `result` field 1 and string `message` field 2.
- `GetCertDataResult final : google::protobuf::Message`: result of fetching currently loaded certificate data. Public field API covers `result` field 1, optional/message `data` field 2 with `has_data`, `mutable_data`, `release_data`, `set_allocated_data`, and string `message` field 3.
- `CertData final : google::protobuf::Message`: simplified certificate model. It exposes `type`, int64 `serial`, subject strings (`organization`, `organizational_unit`, `country`, `locality`, `common_name`, `subject_serial`), timestamp submessages `valid_from` and `valid_until`, repeated string `dns_names`, bool `is_ca`, and optional recursive `parent_data`.
- Standard message APIs are available on every class: `default_instance`, `descriptor`, `GetReflection`, `New`, `CopyFrom`, `MergeFrom`, `Clear`, `ByteSizeLong`, `_InternalSerialize`, `GetCachedSize`, `Swap`, `UnsafeArenaSwap`, unknown-field accessors, and metadata access.

## Control Flow
Most control flow in this header is inline field access and protobuf lifecycle dispatch. Application code constructs a message, mutates fields through generated setters or `mutable_*` methods, and then hands it to protobuf serialization, reflection, or RPC/FFI transport code. Full parse/serialize/merge implementations live in `license.pb.cc`.

Scalar accessors read and write the generated `_impl_` storage directly, with protobuf TSan instrumentation around reads/writes. Enum fields are integer-backed and cast to the enum type on reads. String fields use `ArenaStringPtr`, support templated `set_*` overloads, `mutable_*`, `release_*`, and `set_allocated_*`, and default to protobuf's fixed empty string.

Submessage control flow is presence-aware. `GetCertDataResult::mutable_data()`, `CertData::mutable_valid_from()`, `CertData::mutable_valid_until()`, and `CertData::mutable_parent_data()` lazily allocate submessages on the owning arena and set the relevant has-bit. `clear_*` for these fields clears the submessage if allocated and clears presence. `release_*` returns a heap-safe duplicate when needed for arena-owned data; unsafe arena release/set variants assume caller-managed arena lifetime.

Repeated DNS names use `RepeatedPtrField<std::string>`. Callers can inspect size, index elements, mutate an element, append via `add_dns_names`, replace the full repeated field through `mutable_dns_names`, or clear the list.

## State And Persistence
The header defines the in-memory object layout used by generated C++ code: cached sizes, unknown-field metadata inherited from `Message`, string arena pointers, has-bit bitmaps, repeated fields, raw submessage pointers, scalar values, and boolean flags. It does not itself persist data; persistence is the protobuf wire format implemented by the companion `.cc`.

Wire compatibility depends on stable field numbers and enum numeric values. `VerifyResult` values 0-3 and `CertType` values 0-6 must stay aligned with Go and Rust generated outputs. `CertData` field 13 is a recursive optional `CertData`, allowing issuer/parent certificate chains. `dns_names` field 11 has the proto JSON name `DNSNames`, which matters for JSON mapping compatibility.

Unknown fields are available through `unknown_fields()` and `mutable_unknown_fields()`, so C++ full-runtime messages can preserve fields added by newer schema versions. `IsInitialized()` always returns true because this is proto3 with no required fields.

## Dependencies And Integration Points
- Depends on Protobuf C++ runtime headers, generated-message internals, Abseil string views through protobuf APIs, and `google/protobuf/timestamp.pb.h`.
- Must be compiled with the matching generated implementation `license.pb.cc`; descriptor tables, default instances, parse tables, constructors, destructors, and non-inline methods are defined there.
- Generated from `sources/distributed-fs/beegfs-protobuf/proto/license.proto` by the repository `Makefile`. `make test-protos` regenerates all language outputs and checks that generated files are up to date.
- Integrates with C++ consumers that need BeeGFS license verification results, feature verification status, or certificate metadata. It also aligns with `go/license/license.pb.go`, `go/license/license_protoopaque.pb.go`, and `rust/license.rs`.
- The source proto comment states these messages are used to pass data from the Go library to consumers via CStrings and C FFI, so binary encoding/decoding boundaries are likely more important than direct C++ business logic in this repository.

## Risks And Edge Cases
- Manual edits are not durable. The file is generated and begins with "DO NOT EDIT"; changes should be made in `proto/license.proto` and regenerated.
- The Protobuf version guard is strict. Building with any header/runtime version other than the generated target version (`5029002`) fails at compile time.
- Generated setters do not enforce license-domain semantics. `VerifyCertResult.message` can be non-empty for valid results, `serial` can be empty for valid results, `CertData` can contain default/unspecified certificate types, invalid time ranges, empty subject fields, or arbitrary DNS name strings unless caller validation checks them.
- `*_IsValid` only checks numeric enum ranges. Unknown enum integers can still arrive through protobuf parsing because the generated layout treats enum fields as open enums.
- Recursive `parent_data` needs application-level bounds if data can come from untrusted inputs; the schema can represent long parent chains.
- Arena ownership APIs are easy to misuse. Mixing `set_allocated_*`, `release_*`, and unsafe arena variants across heap and arena instances can create lifetime bugs in user code.
- String fields are protobuf strings with UTF-8 verification during serialization in the implementation. They are not byte fields, so arbitrary certificate-derived bytes should not be stored there unless valid UTF-8.

## Test Signals
- `make test-protos` in `sources/distributed-fs/beegfs-protobuf` is the generated-artifact freshness test and should leave `cpp/license.pb.h`, `cpp/license.pb.cc`, Go output, and Rust output unchanged.
- C++ compile tests should include this header with Protobuf C++ 5.29.2 and link `license.pb.cc`.
- API tests should exercise enum `Name`/`Parse` helpers, every scalar/string accessor, repeated `dns_names`, `has_*` behavior for `data`, timestamps, and `parent_data`, and ownership paths such as `release_*`/`set_allocated_*` on heap and arena messages.
- Wire tests should round-trip representative successful, invalid, and error `VerifyResult` values, `CertType` values, nested issuer certificate data, unknown fields, and JSON mapping for `DNSNames`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/license.pb.h -->
