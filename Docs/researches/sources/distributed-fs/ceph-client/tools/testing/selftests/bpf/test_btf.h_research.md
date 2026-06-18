# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_btf.h

## Research

This header is a compact BTF raw-record construction helper for BPF selftests. It does not implement runtime logic; instead it provides macros that encode BTF type records and their payload words into `__u32` initializer streams used by raw BTF tests. `BTF_END_RAW` is a sentinel used by consumers to find the end of a raw fixture.

The main API surface mirrors kernel BTF kinds: `BTF_INFO_ENC()`, `BTF_TYPE_ENC()`, `BTF_TYPE_INT_ENC()`, `BTF_FWD_ENC()`, `BTF_TYPE_ARRAY_ENC()`, `BTF_STRUCT_ENC()`, `BTF_UNION_ENC()`, `BTF_VAR_ENC()`, `BTF_VAR_SECINFO_ENC()`, `BTF_MEMBER_ENC()`, `BTF_ENUM_ENC()`, `BTF_ENUM64_ENC()`, `BTF_TYPEDEF_ENC()`, pointer/qualifier encoders, function prototype/function encoders, float encoders, declaration-tag encoders, and type-tag encoders. `BTF_MEMBER_OFFSET()` packs bitfield size and bit offset into the member offset representation.

Control flow is entirely compile-time macro expansion. The header depends on BTF constants such as `BTF_KIND_INT`, `BTF_KIND_ARRAY`, and `BTF_MAX_VLEN` being visible to the including source. It has no state, persistence, allocation, or external side effects. Integration points are raw BTF tests that need dense fixture arrays without repeating the low-level bit packing.

Risks are semantic drift when the kernel BTF encoding changes or when a macro silently packs a value that exceeds the expected field width. Because these macros generate binary ABI fixtures, incorrect packing can make downstream tests fail in confusing verifier paths. Test signals come from consumers such as BTF verifier and dedup tests: successful kernel load, expected verifier errors, and exact raw BTF comparisons indirectly validate the macros.
