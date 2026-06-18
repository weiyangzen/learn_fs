# sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c` is generated XDR helper code for selected NFSv4.1 XDR specification types. It provides type-safe decode and encode functions consumed by `nfs4xdr.c` for open-argument capability attributes, delegated timestamp attributes, ACL model/scope enums, and POSIX ACL extension structures. The source was read as a complete 569-line generated file.

## Important APIs, Types, and Functions

The exported functions are `xdrgen_decode_fattr4_open_arguments()`, `xdrgen_encode_fattr4_open_arguments()`, `xdrgen_decode_fattr4_time_deleg_access()`, `xdrgen_encode_fattr4_time_deleg_access()`, `xdrgen_decode_fattr4_time_deleg_modify()`, `xdrgen_encode_fattr4_time_deleg_modify()`, `xdrgen_decode_aclmodel4()`, `xdrgen_encode_aclmodel4()`, `xdrgen_decode_aclscope4()`, `xdrgen_encode_aclscope4()`, `xdrgen_decode_posixacetag4()`, `xdrgen_encode_posixacetag4()`, `xdrgen_decode_posixaceperm4()`, and `xdrgen_encode_posixaceperm4()`.

Internal helpers cover generated primitive aliases (`int64_t`, `uint32_t`, `bitmap4`, UTF-8 string aliases, `nfstime4`), enum decoders for open share access/deny/want/claim/create modes, `open_delegation_type4`, ACL model/scope, POSIX ACE tags, and compound structures such as `open_arguments4`, `posixace4`, `fattr4_posix_default_acl`, and `fattr4_posix_access_acl`.

## Control Flow

Decode helpers read from `struct xdr_stream` in XDR field order and return `false` on short stream, malformed enum value, or failed nested decode. Array helpers first decode `count` and then iterate `count` elements using the generated element decoder. Enum decoders read a `u32`, switch over the allowed constants, reject unknown values, and assign the typed enum only after validation.

Encode helpers mirror the decode layout. They write counts before array elements, serialize enum values as `u32`, encode `nfstime4` as signed seconds plus unsigned nanoseconds, and encode UTF-8 string aliases with `xdr_stream_encode_opaque()`. Public wrappers simply delegate to the generated structure/alias implementation for the corresponding XDR typedef.

## State and Persistence Behavior

The file keeps no global mutable state and performs no persistence. It only advances an XDR stream and populates caller-owned structures or reads caller-owned values. The generated bitmap and array types assume their `element` pointers are supplied by the caller and have enough storage for the decoded `count`; this contract is inherited from the generated XDR type definitions in the included headers.

## Dependencies and Integration Points

The file depends on `linux/sunrpc/svc.h`, `nfs4xdr_gen.h`, generic xdrgen builtins, and generated NFSv4.1 type definitions. Its primary consumer in this subset is `nfs4xdr.c`: delegated time attributes use the generated time decoders, OPEN_ARGUMENTS uses generated bitmap encoders, and POSIX ACL extension decode/encode paths use generated POSIX ACE tag and permission helpers.

Because it is generated from `Documentation/sunrpc/xdr/nfs4_1.x`, the source of truth is the XDR specification and generator, not this C file. Manual edits would be overwritten and should instead be made in the specification or xdrgen tooling.

## Risks and Edge Cases

The biggest risk is array bounds: generated decode loops trust the destination array layout associated with generated `bitmap4` and fattr array types. Callers must provide storage consistent with the decoded count or ensure upstream XDR definitions cap it. Enum decoders are stricter than simple casts, which is good for protocol hardening but can reject values if the XDR specification evolves without regenerating this file.

For encode paths, most enum encoders do not revalidate the enum value and simply write it; callers must avoid passing untrusted or uninitialized enum values. Generated UTF-8 helpers encode opaque bytes and do not validate Unicode semantics. The file uses `__maybe_unused` for many helpers because generation may emit support code for types not currently referenced by NFSD.

## Test Signals

Useful signals are build coverage after regenerating from `nfs4_1.x`, round-trip XDR tests for each exported helper, malformed enum decode tests, array count boundary tests, and integration tests through `nfs4xdr.c` for OPEN_ARGUMENTS, delegated timestamp setattr, and POSIX ACL extension attributes. Static analysis should focus on generated array element storage contracts and return-value handling by callers.
