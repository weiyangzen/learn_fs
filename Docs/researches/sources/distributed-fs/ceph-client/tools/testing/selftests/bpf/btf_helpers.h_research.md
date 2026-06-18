# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/btf_helpers.h

Purpose: public declarations and convenience macro for BTF helper functions.

Important APIs and macros: declares `fprintf_btf_type_raw`, `btf_type_raw_dump`, `btf_validate_raw`, `btf_type_c_dump`, and `VALIDATE_RAW_BTF(btf, raw_types...)`.

Control flow: header only; `VALIDATE_RAW_BTF` constructs an inline expected string array and count.

State and persistence: no header state.

Dependencies and integration points: includes stdio and libbpf BTF headers; pairs with `btf_helpers.c`.

Risks: variadic macro expects string literals/compatible pointers and counts by `sizeof(void *)`, matching pointer arrays.

Test signals: tests use `VALIDATE_RAW_BTF` to compare a whole BTF object in one call.
