# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.c

Purpose: BTF formatting and validation helpers for selftests that compare raw BTF or C dumps.

Important APIs and functions: `fprintf_btf_type_raw()` prints one BTF type by id; `btf_type_raw_dump()` returns a static-buffer raw dump; `btf_validate_raw()` compares all types against expected strings using test assertions; `btf_type_c_dump()` uses `btf_dump` to render C-like declarations. Static helpers map kind, int encoding, var linkage, func linkage, and string offsets.

Control flow: raw dump fetches the type, prints common header, then switches by BTF kind to emit kind-specific fields and children. C dump creates a `btf_dump`, iterates type ids, and writes into a static fmemopen buffer.

State and persistence: static 16 KiB buffers are overwritten on each dump call. No heap state persists beyond a call.

Dependencies and integration points: depends on libbpf BTF APIs, `test_progs.h` assertion macros, `fmemopen`, and BTF kind constants up to ENUM64.

Risks: static buffers are not thread-safe and can truncate large dumps; expected strings are tightly coupled to formatting; new BTF kinds need mapping updates.

Test signals: validation failures identify mismatched raw BTF strings; C dump errors print diagnostic messages.
