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
